import os
import argparse
import pandas as pd

# ================================================
# Utility
# ================================================

def tabstop( s, tabnum = 8, cache = ''):
    if not '\t' in s:
        return cache + s
    tab_index = s.find('\t')
    cache += s[:tab_index]+' '*(tabnum-(tab_index % tabnum))
    return tabstop(s[tab_index+1:], tabnum, cache)

def read_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return lines

# ================================================
# Files procesing
# ================================================

def extract_data(lines):
    data = []
    headers = None
    totallines = len(lines) - 1
    line_index = 0
    while line_index < totallines:

        line = tabstop(lines[line_index])
        if "rows will be truncated" in line:
            line_index += 2

        if not line.strip():  # check empty lines
            if not headers:  # If headers not defined, assume this line is headers
                headers = [header.strip() for header in lines[line_index+1].strip().split()]
                col_lenght = list(map(lambda line: len(line) ,lines[line_index+2].split()))

            line_index += 2

        else:
            row_data = [ line[sum(col_lenght[:i]) + i : sum(col_lenght[:i]) + i + col_lenght[i] ].strip() for i in range(len(col_lenght))]
            data.append(row_data)

        line_index += 1

    return headers, data

def process_file(file_path):
    lines = read_file(file_path)
    headers, data = extract_data(lines)
    df = pd.DataFrame(data, columns=headers)
    return df

def generate_dataframes(folder_path):
    files_to_skip = {"version.txt", "remote_os_auth.txt", "db_links.txt", "audit_trails.txt"}
    files = os.listdir(folder_path)
    dataframes = {}
    for file_name in files:
        if file_name in files_to_skip:
            continue
        print(f"Processing {file_name}")
        file_path = os.path.join(folder_path, file_name)
        df = process_file(file_path)
        dataframes[file_name.split(".")[0]] = df
    return dataframes

# ================================================
# Privileges procesing
# ================================================

# Create a dictionary to store roles and their associated privileges
role_privileges = {}
# Function to recursively find privileges for a given role
def find_roles_privileges(role, privs_df, granted_roles_df, history=''):

    if role in set(history.split("|")):
        return set()

    if role not in role_privileges:

        # Find privileges granted directly to the role
        privileges = set(privs_df.loc[privs_df['GRANTEE'] == role, 'PRIVILEGE'])
        
        # Find roles granted to this role
        sub_roles = set(granted_roles_df.loc[granted_roles_df['GRANTEE'] == role, 'GRANTED_ROLE'])
        
        # Recursively find privileges for each sub-role
        sub_privileges = set([])
        for sub_role in sub_roles:
            sub_privileges = sub_privileges | find_roles_privileges(sub_role, privs_df, granted_roles_df, history+"|"+role)
        
        # Combine privileges from this role and its sub-roles
        role_privileges[role] = privileges.update(sub_privileges)
    
    return role_privileges[role] if role_privileges[role] else set()

# Function to find privileges for a given user
def find_user_privileges(user, privs_df, granted_roles_df):
    # Find privileges directly assigned to the user
    user_privileges = set(privs_df.loc[privs_df['GRANTEE'] == user, 'PRIVILEGE'])
    
    # Find roles assigned to the user
    user_roles = set(granted_roles_df.loc[granted_roles_df['GRANTEE'] == user, 'GRANTED_ROLE'])
    
    # Find privileges assigned through roles
    role_privs = set()
    for role in user_roles:
        role_privs.update(find_roles_privileges(role, privs_df, granted_roles_df))
    
    # Combine privileges from direct assignment and role assignment
    user_privileges.update(role_privs)
    
    return user_privileges

def check_privileges(privileges_set, priv_tuple):
    c = 0
    for priv in priv_tuple:
        if priv in privileges_set:
            c += 1
    return c == len(priv_tuple)

# ================================================
# Roles Procesing
# ================================================

# Function to find privileges for a given user
def find_roles_users(roles, granted_roles_df):
	user_roles.update(set(granted_roles_df.loc[granted_roles_df['GRANTED_ROLE'] == role, 'GRANTEE']))
	return user_privileges

# ================================================
# Audit
# ================================================

def audit_data(dataframes, outfolder):

    # ===============================
    # DataFrames
    # ===============================

    users_df = dataframes["users"]
    lastlogon_df = dataframes["last_logon"]
    privs_df = dataframes["privs"]
    roles_df = dataframes["roles"]
    java_df = dataframes["check_java"]

    # ===============================
    # Audit Logons
    # ===============================

    # Convert 'CREATED' and 'LOGON_TIM' columns to datetime
    users_df['CREATED'] = pd.to_datetime(users_df['CREATED'], format='%d-%b-%y')
    lastlogon_df['LOGON_TIM'] = pd.to_datetime(lastlogon_df['LOGON_TIM'], format='%d-%b-%y')

    # Merge the dataframes on 'USERNAME'
    merged_df = pd.merge(users_df, lastlogon_df, on='USERNAME', how='left')

    # Calculate if the last logon was within the last 12 months
    merged_df['LastLogonWithin12Months'] = merged_df['LOGON_TIM'] >= (pd.to_datetime('now') - pd.DateOffset(months=12))

    # Drop all columns except 'USERNAME' and 'LastLogonWithin12Months'
    merged_df.drop(merged_df.columns.difference(['USERNAME', 'LOGON_TIM', 'LastLogonWithin12Months']), axis=1, inplace=True)
    merged_df.sort_values(by='LOGON_TIM', inplace=True, ascending=False)

    # Print results
    print(" ===== Last Logon =====")
    count_false = merged_df['LastLogonWithin12Months'].value_counts()[False]
    print("Number of entries that has not log in in the last 12 months:", count_false)
    print()
    print(merged_df[merged_df['LastLogonWithin12Months'] == False])
    print()
    merged_df.to_excel(f"{outfolder}/LoginAudit-LastLogonUsers.xslx")

    # ===============================
    # Audit Privileges Scalation to DBA by Privs Combo
    # ===============================

    dangerous_privs = {
        "SELECT_ANY_DICTIONARY": ("SELECT ANY DICTIONARY",),
        "GRANT_ANY_ROLE": ("GRANT ANY ROLE",),
        "ALTER_ANY_ROLE": ("ALTER ANY ROLE",),
        "GRANT_ANY_PRIVILEGE": ("GRANT ANY PRIVILEGE",),
        "ALTER_USER": ("ALTER USER",),
        "BECOME_USER-ALTER_SESSION": ("BECOME USER", "ALTER SESSION",),
        "CREATE_PROCEDURE-EXECUTE_ANY_PROCEDURE": ("CREATE PROCEDURE", "EXECUTE ANY PROCEDURE",),
        "CREATE_PROCEDURE-CREATE_ANY_TRIGGER": ("CREATE PROCEDURE", "CREATE ANY TRIGGER",),
        "CREATE_PROCEDURE-ANALYZE_ANY": ("CREATE PROCEDURE", "ANALYZE ANY",),
        "CREATE_PROCEDURE-CREATE_ANY_INDEX": ("CREATE PROCEDURE", "CREATE ANY INDEX",),
        "UPDATE_PROCEDURE-EXECUTE_ANY_PROCEDURE": ("UPDATE PROCEDURE", "EXECUTE ANY PROCEDURE",),
        "UPDATE_PROCEDURE-CREATE_ANY_TRIGGER": ("UPDATE PROCEDURE", "CREATE ANY TRIGGER",),
        "UPDATE_PROCEDURE-ANALYZE_ANY": ("UPDATE PROCEDURE", "ANALYZE ANY",),
        "UPDATE_PROCEDURE-CREATE_ANY_INDEX": ("UPDATE PROCEDURE", "CREATE ANY INDEX",),
    }

    # Roles Privs

    # Get privs per Role
    roles_privileges_df = roles_df.copy()
    roles_privileges_df['Role_Privileges'] = roles_privileges_df['GRANTED_ROLE'].apply(lambda role: find_roles_privileges(role, privs_df, roles_df))

    roles_privileges_df.drop(roles_privileges_df.columns.difference(['GRANTED_ROLE', 'Role_Privileges']), axis=1, inplace=True)

    # Add columns to roles_df for each tuple in dangerous_privs
    for col_name, priv_tuple in dangerous_privs.items():
        roles_privileges_df[col_name] = roles_privileges_df['Role_Privileges'].apply(lambda priv_set: check_privileges(priv_set, priv_tuple))

    # User Privs

    # Get privs per user considewring roles
    users_privs_df = users_df.copy()
    users_privs_df['User_Privileges'] = users_privs_df['USERNAME'].apply(lambda username: find_user_privileges(username, privs_df, roles_df))
    
    users_privs_df.drop(users_privs_df.columns.difference(['USERNAME', 'User_Privileges']), axis=1, inplace=True)

    # Add columns to users_df for each tuple in dangerous_privs
    for col_name, priv_tuple in dangerous_privs.items():
        users_privs_df[col_name] = users_privs_df['User_Privileges'].apply(lambda priv_set: check_privileges(priv_set, priv_tuple))

    # Print results
    print(" ===== Priviglege Escalation Audit =====")
    dangerous_roles = roles_privileges_df[list(dangerous_privs.keys())].any(axis=1).sum()
    dangerous_users = users_privs_df[list(dangerous_privs.keys())].any(axis=1).sum()
    print("Number of roles with dangerous privileges", dangerous_roles)
    if dangerous_roles > 0:
        print()
        print(roles_privileges_df[roles_privileges_df[list(dangerous_privs.keys())].any(axis=1)])
        print()
        roles_privileges_df.to_excel(f"{outfolder}/DB_PrivsAudit-Roles.xslx")
    print("Number of users with dangerous privileges", dangerous_users)
    if dangerous_users > 0:
        print()
        print(users_privs_df[users_privs_df[list(dangerous_privs.keys())].any(axis=1)])
        print()
        users_privs_df.to_excel(f"{outfolder}/DB_PrivsAudit-Users.xslx")

    # ===============================
    # Proxy users
    # ===============================

    # ToDo

    # ===============================
    # Java to OS
    # ===============================

    dangerous_java_roles = [
        "JAVASYSPRIV",
        "JAVA_ADMIN",
        "JAVADEBUGPRIV"
    ]

    java_options = java_df.to_dict(orient="index")
    if len(java_options) > 0:
        


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument("-f", "--folder-path", type=str, help='Path to the folder containing .txt files', required=True)
    parser.add_argument("-o", "--out-folder-path", type=str, help='Path to the folder containing .txt files')
    parser.add_argument('-v', '--verbose', help="Verbosity Level. (-v to -vvv)", action='count', default=0)
    args = parser.parse_args()

    out_folder_path = args.out_folder_path if args.out_folder_path else args.folder_path+"_report"

    dataframes = generate_dataframes(args.folder_path)

    audit_data(dataframes, out_folder_path)

    for name, dataframe in dataframes.items():
        print(" ========================= ")
        print(name)
        print()
        print(dataframe.head())
        print()
