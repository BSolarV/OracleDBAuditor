import os
import shutil
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
		if "rows will be truncated" in line.lower():
			line_index += 1

		elif not line.strip():  # check empty lines
			if not headers:  # If headers not defined, assume this line is headers
				print("[-] Found empty line")
				print(f"[+] {lines[line_index]}")
				print(f"[+] {lines[line_index+1]}")
				print(f"[+] {lines[line_index+2]}")
				headers = [header.strip() for header in lines[line_index+1].strip().split()]
				col_lenght = list(map(lambda line: len(line) ,lines[line_index+2].split()))

			line_index += 1

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
	files_to_skip = {"version.txt", "remote_os_auth.txt", "pass_policy.txt", "db_links.txt"}
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
	user_roles = {}
	for role in roles:
		users = list(granted_roles_df.loc[granted_roles_df['GRANTED_ROLE'] == role, 'GRANTEE'])
		for user in users:
			if user not in user_roles:
				user_roles[user] = list()
			user_roles[user].append(role)
	return user_roles

# ================================================
# Tab Privs Processing
# ================================================

# Function to find privileges for a given user
def find_roles_users(roles, granted_roles_df):
	user_roles = {}
	for role in roles:
		users = list(granted_roles_df.loc[granted_roles_df['GRANTED_ROLE'] == role, 'GRANTEE'])
		for user in users:
			if user not in user_roles:
				user_roles[user] = list()
			user_roles[user].append(role)
	return user_roles

# ================================================
# Privs Auditing
# ================================================
#def check_priv_audited(username, priv, stm_audit_df):
#	stm_audit_df.loc[stm_audit_df['username'] == username | stm_audit_df['username']]

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
	dba_registry_df = dataframes["dba_registry"]
	public_tab_pirvs_df = dataframes["public_tab_privs"]
	tab_pirvs_df = dataframes["procedures_privs"]
	parameters_df = dataframes["every_parameter"]
	dba_users_df = dataframes["dba_users"]
	proxy_users_df = dataframes["proxy_users"]
	audit_trails_config_df = dataframes["audit_trails_config"]
	audit_trails_users_statements_df = dataframes["audit_trails_users_statements"]
	audit_trails_users_objects_df = dataframes["audit_trails_users_objects"]

	if not os.path.exists(out_folder_path+"/raw_data"):
		os.makedirs(out_folder_path+"/raw_data")

	users_df.to_excel(out_folder_path+"/raw_data/users_df.xlsx")
	lastlogon_df.to_excel(out_folder_path+"/raw_data/lastlogon_df.xlsx")
	privs_df.to_excel(out_folder_path+"/raw_data/privs_df.xlsx")
	roles_df.to_excel(out_folder_path+"/raw_data/roles_df.xlsx")
	dba_registry_df.to_excel(out_folder_path+"/raw_data/dba_registry_df.xlsx")
	public_tab_pirvs_df.to_excel(out_folder_path+"/raw_data/public_tab_pirvs_df.xlsx")
	tab_pirvs_df.to_excel(out_folder_path+"/raw_data/tab_pirvs_df.xlsx")
	parameters_df.to_excel(out_folder_path+"/raw_data/parameters_df.xlsx")
	dba_users_df.to_excel(out_folder_path+"/raw_data/dba_users_df.xlsx")
	proxy_users_df.to_excel(out_folder_path+"/raw_data/proxy_users_df.xlsx")
	audit_trails_config_df.to_excel(out_folder_path+"/raw_data/audit_trails_config_df.xlsx")
	audit_trails_users_statements_df.to_excel(out_folder_path+"/raw_data/audit_trails_users_statements_df.xlsx")
	audit_trails_users_objects_df.to_excel(out_folder_path+"/raw_data/audit_trails_users_objects_df.xlsx")

	# ===============================
	# Adding usefull info to users
	# ===============================
	system_users = set(('SYS','OUTLN','SYSTEM','PERFSTAT', 'ANONYMOUS',  'APEX_040200',  'APEX_PUBLIC_USER',  'APPQOSSYS',  'AUDSYS',  'CTXSYS',  'DBSNMP',  'DIP',  'DVF',  'DVSYS',  'EXFSYS',  'FLOWS_FILES',  'GSMADMIN_INTERNAL',  'GSMCATUSER',  'GSMUSER',  'LBACSYS',  'MDDATA',  'MDSYS',  'ORACLE_OCM',  'ORDDATA',  'ORDPLUGINS',  'ORDSYS',  'OUTLN',  'SI_INFORMTN_SCHEMA',  'SPATIAL_CSW_ADMIN_USR',  'SPATIAL_WFS_ADMIN_USR',  'SYS',  'SYSBACKUP',  'SYSDG',  'SYSKM',  'SYSTEM',  'WMSYS',  'XDB',  'XS$NULL',  'OLAPSYS',  'OJVMSYS',  'DV_SECANALYST') )
	users_df["is_system_user"] = users_df["USERNAME"].apply(lambda username: True if username in system_users else False)

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
		"CREATE_TABLE-CREATE_ANY_DIRECTORY": ("CREATE TABLE", "CREATE ANY DIRECTORY")
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

	users_privs_df.to_excel(f"{outfolder}/Users.xlsx")
		
	users_privs_df.drop(users_privs_df.columns.difference(['USERNAME', "is_system_user", 'ACCOUNT_STATUS', 'User_Privileges']), axis=1, inplace=True)

	users_dangerous_privs_df = users_privs_df.copy()

	critical_privs = set(('ALTER','WRITE','INSERT','DELETE','UPDATE','BECOME USER','ALTER ANY MATERIALIZED VIEW','ALTER ANY ROLE','ALTER ANY TABLE','ALTER DATABASE','ALTER SESSION','ALTER SYSTEM','ALTER USER','CREATE ANY JOB','CREATE ANY MATERIALIZED VIEW','CREATE ANY PROCEDURE','CREATE ANY TABLE','CREATE ANY VIEW','CREATE MATERIALIZED VIEW','CREATE PROCEDURE','CREATE ROLE','CREATE TABLE','CREATE USER','CREATE VIEW','DELETE ANY TABLE','DROP ANY MATERIALIZED VIEW','DROP ANY ROLE','DROP ANY TABLE','DROP ANY VIEW','DROP PUBLIC DATABASE LINK','DROP USER','EXPORT FULL DATABASE','GRANT ANY OBJECT PRIVILEGE','GRANT ANY PRIVILEGE','GRANT ANY ROLE','INSERT ANY TABLE','MERGE ANY VIEW','UPDATE ANY TABLE'))
	users_dangerous_privs_df["has_critical_privs"] = users_dangerous_privs_df["User_Privileges"].apply(lambda privs_set: True if sum([ 1 for priv in privs_set if priv in critical_privs ]) > 0 else False)

	for col_name, priv_tuple in dangerous_privs.items():
		users_dangerous_privs_df[col_name] = users_dangerous_privs_df['User_Privileges'].apply(lambda priv_set: check_privileges(priv_set, priv_tuple))

	# Print results
	print(" ===== Priviglege Escalation Audit =====")
	dangerous_roles = roles_privileges_df[list(dangerous_privs.keys())].any(axis=1).sum()
	dangerous_users = users_dangerous_privs_df[list(dangerous_privs.keys())].any(axis=1).sum()
	print("Number of roles with dangerous privileges", dangerous_roles)
	if dangerous_roles > 0:
		print()
		print(roles_privileges_df[roles_privileges_df[list(dangerous_privs.keys())].any(axis=1)])
		print()
		roles_privileges_df[roles_privileges_df[list(dangerous_privs.keys())].any(axis=1)].to_excel(f"{outfolder}/DBPrivsAudit-Roles.xlsx")
	print("Number of users with dangerous privileges", dangerous_users)
	if dangerous_users > 0:
		print()
		print(users_dangerous_privs_df[users_dangerous_privs_df[list(dangerous_privs.keys())].any(axis=1)])
		print()
		users_dangerous_privs_df[users_dangerous_privs_df[list(dangerous_privs.keys())].any(axis=1)].to_excel(f"{outfolder}/DBPrivsAudit-Users.xlsx")
	privs_df.to_excel(f"{outfolder}/DBPrivsAudit-EveryUser.xlsx")

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
	merged_df.drop(merged_df.columns.difference(['USERNAME', "is_system_user", 'LOGON_TIM', 'LastLogonWithin12Months']), axis=1, inplace=True)
	merged_df.sort_values(by='LOGON_TIM', inplace=True, ascending=False)

	# Print results
	print(" ===== Last Logon =====")
	count_false = merged_df['LastLogonWithin12Months'].value_counts()[False]
	print("Number of entries that has not log in in the last 12 months:", count_false)
	print()
	print(merged_df[merged_df['LastLogonWithin12Months'] == False])
	print()
	merged_df = pd.merge(merged_df, users_privs_df, on='USERNAME', how='left')
	merged_df.to_excel(f"{outfolder}/LoginAudit-LastLogonUsers.xlsx")

	# ===============================
	# Proxy users
	# ===============================

	print("Number of proxy users found:", len(proxy_users_df))
	if len(proxy_users_df) > 0:
		print()
		print(proxy_users_df)
		print()
		proxy_users_df.to_excel(f"{outfolder}/ProxyUsers.xlsx")

	# ===============================
	# Regisry Check
	# ===============================
 
	print("Number of installed components:", len(dba_registry_df))
	if len(dba_registry_df) > 0:
		print()
		print(dba_registry_df)
		print()
		dba_registry_df.to_excel(f"{outfolder}/InstalledComponents.xlsx")

	# ===============================
	# Java to OS
	# ===============================

	dangerous_java_roles = [
		"JAVASYSPRIV",
		"JAVA_ADMIN",
		"JAVADEBUGPRIV"
	]

	java_options = dba_registry_df[dba_registry_df["COMP_NAME"].str.lower().contains("java")].to_dict(orient="index")
	java_versions = [ java["COMP_NAME"] + f"[{java['VERSION']}]" for java in java_options.values() ]
	print(f"Amount of Java VMs found: {len(java_versions)}.")
	if len(java_versions) > 0:
		for java_version in java_versions:
			print(f"	{java_version}")
		
		print()

		javaroles_by_users = find_roles_users(dangerous_java_roles, roles_df)
		print("Number of users that can execute commands via java:", len(javaroles_by_users))
		if len(javaroles_by_users) > 0:
			java_users_df = pd.DataFrame.from_dict( {"username": list(javaroles_by_users.keys()), "roles": list(javaroles_by_users.values())} )
			print()
			print(java_users_df)
			print()
			java_users_df.to_excel(f"{outfolder}/JavaAudit.xlsx")
		

	# ===============================
	# Dangerous Tab Privs
	# ===============================
 
	dangerous_tab_privs = set([
		"UTL_FILE",
		"UTL_HTTP",
		"UTL_SMTP",
		"UTL_TCP",
		"DBMS_JAVA",
		"DBMS_JOB",
		"DBMS_SQ",
		"DBMS_SCHEDULER",
		"DBMS_ADVISOR",
		"DBMS_XSLPROCESSOR",
		"DBMS_LOB",
		"DBMS_OBFUSCATION_TOOLKIT",
		"OWA_UTIL",
	])
	
	public_tab_pirvs_df
	tab_pirvs_df

	# Check for tab privs on public 
	exposed_tab_privs = public_tab_pirvs_df[public_tab_pirvs_df["TABLE_NAME"].isin(dangerous_tab_privs)]

	# Print public tab privs
	print(f"Number of dangerous Tab Privs asigned to Public: {len(exposed_tab_privs)}")
	if len(exposed_tab_privs) > 0:
		print()
		print(exposed_tab_privs)
		print()
		exposed_tab_privs.to_excel(f"{outfolder}/TabPrivs-Public.xlsx")

	# Check for tab privs on users 
	users_tab_privs = tab_pirvs_df[tab_pirvs_df["GRANTEE"] != "Public"]

	# Print public tab privs
	print(f"Number of users with dangerous Tab Privs: {len(users_tab_privs)}")
	if len(users_tab_privs) > 0:
		print()
		print(users_tab_privs)
		print()
		users_tab_privs.to_excel(f"{outfolder}/TabPrivs-Users.xlsx")

	# ===============================
	# Parameters check
	# ===============================
 
	parameters_check_df = parameters_df[parameters_df["NAME"].isin(["O7_DICTIONARY_ACCESSIBILITY", "remote_os_authent", "remote_os_role"])]
	print(f"Missconfigurated Parameters: {len(parameters_check_df[parameters_check_df['VALUE'] == True])}")
	parameters_check_df.to_excel(f"{outfolder}/Parameters.xlsx")

	# ===============================
	# Audit Trails
	# ===============================
 
	# Audit settings ("Audit_trail" should be set to "OS" or "DB" and "audit_sys_operations" should be set to "TRUE")
	audit_config_values = {}
	audit_config_values["audit_sys_operations"] = {
		"value": audit_trails_config_df.loc[audit_trails_config_df['NAME'] == "audit_sys_operations"]["VALUE"].iloc[0],
		"text": "OK" if audit_trails_config_df.loc[audit_trails_config_df['NAME'] == "audit_sys_operations"]["VALUE"].iloc[0] == True else "Not OK, should be TRUE."
	}
	audit_config_values["audit_trail"] = {
		"value": audit_trails_config_df.loc[audit_trails_config_df['NAME'] == "audit_trail"]["VALUE"].iloc[0],
		"text": "OK" if audit_trails_config_df.loc[audit_trails_config_df['NAME'] == "audit_trail"]["VALUE"].iloc[0].split(",")[0].strip() in ("DB", "OS") else "Not OK, should be DB or OS."
	}

	print(f"DB Audit - Audit Sys Operations: {audit_config_values['audit_sys_operations']['value']} ({audit_config_values['audit_sys_operations']['text']})")
	print(f"DB Audit - Audit Trail: {audit_config_values['audit_trail']['value']} ({audit_config_values['audit_trail']['text']})")
	print()

	# Current system privileges being audited across the system and by user;

	
 
	# Check current system auditing options across the system and the user;



if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Process some files.')
	parser.add_argument("-f", "--folder-path", type=str, help='Path to the folder containing .txt files', required=True)
	parser.add_argument("-o", "--out-folder-path", type=str, help='Path to the folder containing .txt files')
	parser.add_argument('-v', '--verbose', help="Verbosity Level. (-v to -vvv)", action='count', default=0)
	args = parser.parse_args()

	out_folder_path = args.out_folder_path if args.out_folder_path else args.folder_path+"-Audit"
	
	if not os.path.exists(out_folder_path):
		os.makedirs(out_folder_path)

	files_to_copy = [
		("version.txt", "Version.txt"), 
		("remote_os_auth.txt", "Remote-OS-Auth.txt"), 
		("pass_policy.txt", "PasswordPolicy.txt"), 
		("db_links.txt", "DB_Links.txt")
	]
	for src,dst in files_to_copy:
		shutil.copy(args.folder_path+"/"+src, out_folder_path+"/"+dst)

	dataframes = generate_dataframes(args.folder_path)

	audit_data(dataframes, out_folder_path)