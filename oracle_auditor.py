import os
import shutil
import argparse
import pandas as pd

OUTPUT_WITH = 64

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
	totallines = len(lines)
	line_index = 0
	while line_index < totallines:

		line = tabstop(lines[line_index])
		if "rows will be truncated" in line.lower():
			line_index += 1
		elif "selected." in line.lower():
			pass

		elif not line.strip():  # check empty lines
			if not headers:  # If headers not defined, assume this line is headers
				#print("[-] Found empty line")
				#print(f"[+] {lines[line_index]}")
				#print(f"[+] {lines[line_index+1]}")
				#print(f"[+] {lines[line_index+2]}")
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

def generate_dataframes(folder_path, files_to_skip):
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
		privileges.update(sub_privileges)
		role_privileges[role] = privileges
		
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

	version_df = dataframes["version"]
	patches_df = dataframes["version_patches"]
	pass_policy_df = dataframes["pass_policy"]
	users_df = dataframes["users"]
	lastlogon_df = dataframes["last_logon"]
	privs_df = dataframes["privs"]
	roles_df = dataframes["roles"]
	dba_registry_df = dataframes["dba_registry"]
	tab_pirvs_df = dataframes["procedures_privs"]
	parameters_df = dataframes["every_parameter"]
	dba_users_df = dataframes["dba_users"]
	remote_os_auth_users_df = dataframes["remote_os_auth_users"]
	proxy_users_df = dataframes["proxy_users"]
	db_links_df = dataframes["db_links_all"]
	audit_trails_users_statements_df = dataframes["audit_trails_users_statements"]
	audit_trails_users_objects_df = dataframes["audit_trails_users_objects"]

	if not os.path.exists(out_folder_path+"/raw_data"):
		os.makedirs(out_folder_path+"/raw_data")
		
	for df_name, dataframe in dataframes.items():
		dataframe.to_excel(out_folder_path+f"/raw_data/{df_name}.xlsx")

	# ===============================
	# Database version and patches
	# ===============================
	
	db_version_str = ""

	db_version_str += "".center(OUTPUT_WITH, "=") + "\n"
	db_version_str += " Database version ".center(OUTPUT_WITH, "=") + "\n"
	db_version_str += "".center(OUTPUT_WITH, "=") + "\n"

	db_version_str += version_df.to_string(index=False) + "\n"
	db_version_str += "" + "\n"
	db_version_str += "[+] Patches installed" + "\n"
	db_version_str += patches_df.to_string(index=False) + "\n"

	print(db_version_str)

	with open(outfolder+"/DB_Version.txt", "w") as f:
		f.write(db_version_str)

	# ===============================
	# Password Policy
	# ===============================
	
	pass_policy_str = ""

	pass_policy_str += "".center(OUTPUT_WITH, "=") + "\n"
	pass_policy_str += " Password Policy ".center(OUTPUT_WITH, "=") + "\n"
	pass_policy_str += "".center(OUTPUT_WITH, "=") + "\n"

	pass_policy_str += pass_policy_df.to_string(index=False) + "\n"
	pass_policy_str += "\n"
	pass_policy_str += "[+] Password Policy function" + "\n"
	
	pass_policy_funct_file = "".join(open(outfolder+"/pass_policy_function.txt", "r").readlines())
	pass_policy_str += pass_policy_funct_file

	pass_policy_str += "\n"

	print(pass_policy_str)

	with open(outfolder+"/DB_passploicy.txt", "w") as f:
		f.write(pass_policy_str)

	# ===============================
	# Adding usefull info to users
	# ===============================
	system_users = set(('SYS','OUTLN','SYSTEM','PERFSTAT', 'ANONYMOUS',  'APEX_040200',  'APEX_PUBLIC_USER',  'APPQOSSYS',  'AUDSYS',  'CTXSYS',  'DBSNMP',  'DIP',  'DVF',  'DVSYS',  'EXFSYS',  'FLOWS_FILES',  'GSMADMIN_INTERNAL',  'GSMCATUSER',  'GSMUSER',  'LBACSYS',  'MDDATA',  'MDSYS',  'ORACLE_OCM',  'ORDDATA',  'ORDPLUGINS',  'ORDSYS',  'OUTLN',  'SI_INFORMTN_SCHEMA',  'SPATIAL_CSW_ADMIN_USR',  'SPATIAL_WFS_ADMIN_USR',  'SYSMAN',  'SYSBACKUP',  'SYSDG',  'SYSKM',  'SYSTEM', 'SYSADM', 'WMSYS',  'XDB',  'XS$NULL',  'OLAPSYS',  'OJVMSYS',  'DV_SECANALYST') )
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

	roles_privileges_df["CAN_ELEVATE_PRIVS"] = roles_privileges_df[list(dangerous_privs.keys())[1:]].any(axis=1)
	
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
	
	users_dangerous_privs_df["CAN_ELEVATE_PRIVS"] = users_dangerous_privs_df[list(dangerous_privs.keys())[1:]].any(axis=1)

	roles_privileges_df = roles_privileges_df.drop_duplicates(subset=["GRANTED_ROLE"])
	users_dangerous_privs_df = users_dangerous_privs_df.drop_duplicates(subset=["USERNAME"])

	# Print results
	priv_esc_str = ""

	priv_esc_str += "".center(OUTPUT_WITH, "=") + "\n"
	priv_esc_str += " Priviglege Escalation Audit ".center(OUTPUT_WITH, "=") + "\n"
	priv_esc_str += "".center(OUTPUT_WITH, "=") + "\n"

	dangerous_roles = roles_privileges_df[list(dangerous_privs.keys())].any(axis=1).sum()
	dangerous_users = users_dangerous_privs_df[list(dangerous_privs.keys())].any(axis=1).sum()
	
	if dangerous_roles > 0:
		
		priv_esc_str += f"[+] Number of roles with dangerous privileges: {dangerous_roles}" + "\n"
		priv_esc_str += "\n"
		priv_esc_str += roles_privileges_df[roles_privileges_df[list(dangerous_privs.keys())].any(axis=1)][["GRANTED_ROLE", "SELECT_ANY_DICTIONARY", "CAN_ELEVATE_PRIVS"]].to_string() + "\n"
		priv_esc_str += "\n"
		priv_esc_str += f"More details can be fount at {outfolder}/DBPrivsAudit-Roles.xlsx." + "\n"
		priv_esc_str += "\n"
		roles_privileges_df[roles_privileges_df[list(dangerous_privs.keys())].any(axis=1)].to_excel(f"{outfolder}/DBPrivsAudit-Roles.xlsx")
		
	priv_esc_str += f"[+] Number of users with dangerous privileges: {dangerous_users}" + "\n"

	priv_esc_str += "\n"

	if dangerous_users > 0:
		priv_esc_str += f"[-] Users that can dump password hashes:\n"

		users_dangerous_privs_dict = users_dangerous_privs_df[(users_dangerous_privs_df["SELECT_ANY_DICTIONARY"].eq(True) & users_dangerous_privs_df["is_system_user"].eq(False))].to_dict("index")

		for index in users_dangerous_privs_dict:
			priv_esc_str += f"{users_dangerous_privs_dict[index]['USERNAME']}" + "\n"
			for key in dangerous_privs:
				if key == "SELECT_ANY_DICTIONARY":
					priv_esc_str += f"	- {' + '.join(dangerous_privs[key])}" + "\n"
		
		priv_esc_str += "\n"
		
		priv_esc_str += f"[-] Users that can elevate privileges:" + "\n"
		
		users_dangerous_privs_dict = users_dangerous_privs_df.loc[(users_dangerous_privs_df["CAN_ELEVATE_PRIVS"].eq(True) & users_dangerous_privs_df["is_system_user"].eq(False))].to_dict("index")
		for index in users_dangerous_privs_dict:
			priv_esc_str += f"{users_dangerous_privs_dict[index]['USERNAME']}" + "\n"
			for key in dangerous_privs:
				if key == "SELECT_ANY_DICTIONARY":
					continue
				if users_dangerous_privs_dict[index][key] == True:
					priv_esc_str += f"	- {' + '.join(dangerous_privs[key])}" + "\n"
		
		priv_esc_str += "\n"
		
		users_dangerous_privs_df[users_dangerous_privs_df[list(dangerous_privs.keys())].any(axis=1)].to_excel(f"{outfolder}/DBPrivsAudit-Users.xlsx")

	privs_df.to_excel(f"{outfolder}/DBPrivsAudit-EveryUser.xlsx")

	print(priv_esc_str)

	with open(outfolder+"/DB_PrivsAudit.txt", "w") as f:
		f.write(priv_esc_str)

	# ===============================
	# DBA Users
	# ===============================
 
	dba_users_str = ""

	dba_users_str += "".center(OUTPUT_WITH, "=") + "\n"
	dba_users_str += " DBA Users ".center(OUTPUT_WITH, "=") + "\n"
	dba_users_str += "".center(OUTPUT_WITH, "=") + "\n"

	merged_dba_users_df = pd.merge(dba_users_df, users_df, on='USERNAME', how='left')

	dba_users_str += merged_dba_users_df[["USERNAME", "ACCOUNT_STATUS", "is_system_user"]].to_string() + "\n"

	# ===============================
	# Dangerous Tab Privs
	# ===============================
 
	tab_pirvs_str = ""

	tab_pirvs_str += "".center(OUTPUT_WITH, "=") + "\n"
	tab_pirvs_str += " Dangerous Tab Privs ".center(OUTPUT_WITH, "=") + "\n"
	tab_pirvs_str += "".center(OUTPUT_WITH, "=") + "\n"

	# Check for tab privs on public 
	exposed_tab_privs = tab_pirvs_df[tab_pirvs_df['GRANTEE'] == "PUBLIC"]
	#exposed_tab_privs = public_tab_pirvs_df[public_tab_pirvs_df["TABLE_NAME"].isin(dangerous_tab_privs)]
	
	# Print public tab privs
	tab_pirvs_str += f"[+] Number of dangerous Tab Privs asigned to Public: {len(exposed_tab_privs)}" + "\n"
	if len(exposed_tab_privs) > 0: 
		tab_pirvs_str += "\n"
		tab_pirvs_str += exposed_tab_privs.to_string() + "\n"
		tab_pirvs_str += "\n"
		exposed_tab_privs.to_excel(f"{outfolder}/TabPrivs-Public.xlsx")
		
	# Check for tab privs on users 
	full_tab_pirvs_df = pd.merge(tab_pirvs_df, users_df[["USERNAME", "ACCOUNT_STATUS", "is_system_user"]], how='left', left_on = 'GRANTEE', right_on = 'USERNAME').drop(columns='USERNAME')
	users_tab_privs = full_tab_pirvs_df[full_tab_pirvs_df["GRANTEE"] != "PUBLIC"]

	# Print users with tab privs
	tab_pirvs_str += f"[+] Number of dangerous Tab Privs granted: {len(users_tab_privs)}" + "\n"
	if len(users_tab_privs) > 0:
		users_dangerous_tab_privs_dict = users_tab_privs[users_tab_privs["is_system_user"] == False].to_dict(orient="index")
		users_dangerous_tab_privs_dict_parsed = {}
		for index in users_dangerous_tab_privs_dict:
			if users_dangerous_tab_privs_dict[index]["GRANTEE"] not in users_dangerous_tab_privs_dict_parsed:
				users_dangerous_tab_privs_dict_parsed[users_dangerous_tab_privs_dict[index]["GRANTEE"]] = set([])
			users_dangerous_tab_privs_dict_parsed[users_dangerous_tab_privs_dict[index]["GRANTEE"]].add(users_dangerous_tab_privs_dict[index]["TABLE_NAME"])
		for username in users_dangerous_tab_privs_dict_parsed:
			tab_pirvs_str += username + "\n"
			for tab_priv in users_dangerous_tab_privs_dict_parsed[username]:
				tab_pirvs_str += f"	- {tab_priv}" + "\n"
		tab_pirvs_str += "\n"
		users_tab_privs.to_excel(f"{outfolder}/TabPrivs-Users.xlsx")

	print(tab_pirvs_str)

	with open(outfolder+"/DB_TabPrivs.txt", "w") as f:
		f.write(tab_pirvs_str)
	
	# ===============================
	# Audit Logons
	# ===============================

	# Convert 'CREATED' and 'LOGON_TIM' columns to datetime
	users_df['CREATED'] = pd.to_datetime(users_df['CREATED'], format='%d-%b-%y', utc=True)
	lastlogon_df['LOGON_TIM'] = pd.to_datetime(lastlogon_df['LOGON_TIM'], format='%d-%b-%y', utc=True)

	# Merge the dataframes on 'USERNAME'
	merged_df = pd.merge(users_df, lastlogon_df, on='USERNAME', how='left')

	# Calculate if the last logon was within the last 12 months
	merged_df['LastLogonWithin12Months'] = merged_df['LOGON_TIM'] >= (pd.to_datetime('now', utc=True) - pd.DateOffset(months=12))

	# Drop all columns except 'USERNAME' and 'LastLogonWithin12Months'
	merged_df.drop(merged_df.columns.difference(['USERNAME', "is_system_user", 'LOGON_TIM', 'LastLogonWithin12Months']), axis=1, inplace=True)
	merged_df.sort_values(by='LOGON_TIM', inplace=True, ascending=False)

	merged_df['LOGON_TIM'] = merged_df['LOGON_TIM'].dt.tz_localize(None)

	# Print results
	logon_audit_str = ""

	logon_audit_str += "".center(OUTPUT_WITH, "=") + "\n"
	logon_audit_str += " Last Login Audit ".center(OUTPUT_WITH, "=") + "\n"
	logon_audit_str += "".center(OUTPUT_WITH, "=") + "\n"

	count_false = merged_df['LastLogonWithin12Months'].value_counts()[False]
	logon_audit_str += f"[+] Number of entries that has not log in in the last 12 months: {count_false}" + "\n"
	logon_audit_str += "\n"
	logon_audit_str += merged_df[merged_df['LastLogonWithin12Months'] == False].to_string(index=False) + "\n"
	logon_audit_str += "\n"
	merged_df = pd.merge(merged_df, users_privs_df, on='USERNAME', how='left')
	merged_df.to_excel(f"{outfolder}/LoginAudit-LastLogonUsers.xlsx")
	print(logon_audit_str)

	# ===============================
	# Proxy users
	# ===============================

	proxy_users_str = ""

	proxy_users_str += "".center(OUTPUT_WITH, "=") + "\n"
	proxy_users_str += " Proxy Users ".center(OUTPUT_WITH, "=") + "\n"
	proxy_users_str += "".center(OUTPUT_WITH, "=") + "\n"

	proxy_users_str += f"[+] Number of proxy users found: {len(proxy_users_df)}" + "\n"
	if len(proxy_users_df) > 0:
		proxy_users_str += "\n"
		proxy_users_str += proxy_users_df.to_string() + "\n"
		proxy_users_str += "\n"
		proxy_users_df.to_excel(f"{outfolder}/ProxyUsers.xlsx")

	print(proxy_users_str)

	with open(outfolder+"/DB_LastLoginAudit.txt", "w") as f:
		f.write(proxy_users_str)

	# ===============================
	# DB Links
	# ===============================
 
	db_links_str = ""

	db_links_str += "".center(OUTPUT_WITH, "=") + "\n"
	db_links_str += " Database Links ".center(OUTPUT_WITH, "=") + "\n"
	db_links_str += "".center(OUTPUT_WITH, "=") + "\n"

	public_db_links_df = db_links_df[db_links_df["OWNER"] == "PUBLIC"]
 
	db_links_str += f"[+] Number of PUBLIC DB Links: {len(public_db_links_df)}" + "\n"
	if len(public_db_links_df) > 0:
		db_links_str += "\n"
		db_links_str += public_db_links_df[["OWNER", "USERNAME", "HOST"]].to_string() + "\n"
		db_links_str += "\n"
		public_db_links_df.to_excel(f"{outfolder}/PublicDBLinks.xlsx")

	dangerous_db_links_df = db_links_df[db_links_df["USERNAME"].isin(system_users)]

	db_links_str += f"[+] Number of DB Links to System Users: {len(dangerous_db_links_df)}" + "\n"
	if len(public_db_links_df) > 0:
		db_links_str += "\n"
		db_links_str += dangerous_db_links_df[["OWNER", "USERNAME", "HOST"]].to_string() + "\n"
		db_links_str += "\n"
		db_links_df.to_excel(f"{outfolder}/DBLinks.xlsx")
	
	print(db_links_str)

	with open(outfolder+"/DB_Links.txt", "w") as f:
		f.write(db_links_str)


	# ===============================
	# Remote auth
	# ===============================

	remote_auth_str = ""

	remote_auth_str += "".center(OUTPUT_WITH, "=") + "\n"
	remote_auth_str += " Remote Auth ".center(OUTPUT_WITH, "=") + "\n"
	remote_auth_str += "".center(OUTPUT_WITH, "=") + "\n"

	remote_auth_parameters_check = {
		"remote_os_roles": lambda value: "OK" if value == False else "Not OK. Should be FALSE.", 
		"remote_os_authent": lambda value: "OK" if value == False else "Not OK. Should be FALSE.", 
		"os_authent_prefix": lambda value: "Validate if there are users available.", 
		"ldap_directory_access": lambda value: "OK" if str(value).lower() in ("none", "false") else "Not OK. Should be NONE.", 
		"ldap_directory_sysauth": lambda value: "OK" if str(value).lower() in ("none", "false") else "Not OK. Should be NONE.", 
	}
	remote_auth_parameters_df = parameters_df[parameters_df["NAME"].isin(["remote_os_roles", "remote_os_authent", "os_authent_prefix", "ldap_directory_access", "ldap_directory_sysauth"])]
	remote_auth_parameters_dict = remote_auth_parameters_df.to_dict(orient="index")
	
	remote_auth_str += f"[+] Remote OS Auth parameters:" + "\n"
	for dictionary in remote_auth_parameters_dict.values():
		name = dictionary["NAME"]
		value = dictionary["VALUE"]
		remote_auth_str += f"{name}\tvalue:{value}\t({remote_auth_parameters_check[name](value)})" + "\n"

	remote_auth_str += f"[+] Remote OS Auth available users: {len(remote_os_auth_users_df)}" + "\n"
	if len(remote_os_auth_users_df) > 0:
		remote_auth_str += "\n"
		remote_auth_str += remote_os_auth_users_df.to_string() + "\n"
		remote_auth_str += "\n"

	print(remote_auth_str)

	with open(outfolder+"/DB_RemoteAuth.txt", "w") as f:
		f.write(remote_auth_str)
	
	# ===============================
	# Regisry Check
	# ===============================
 
	installed_components_str = ""

	installed_components_str += "".center(OUTPUT_WITH, "=") + "\n"
	installed_components_str += " Installed Components ".center(OUTPUT_WITH, "=") + "\n"
	installed_components_str += "".center(OUTPUT_WITH, "=") + "\n"
 
	installed_components_str += f"[+] Number of installed components: {len(dba_registry_df)}" + "\n"
	if len(dba_registry_df) > 0:
		installed_components_str += "\n"
		installed_components_str += dba_registry_df.to_string() + "\n"
		installed_components_str += "\n"
		dba_registry_df.to_excel(f"{outfolder}/InstalledComponents.xlsx")
	
	print(installed_components_str)

	with open(outfolder+"/DB_InstalledComponents.txt", "w") as f:
		f.write(installed_components_str)

	# ===============================
	# Java to OS
	# ===============================

	dangerous_java_roles = [
		"JAVASYSPRIV",
		"JAVA_ADMIN",
		"JAVADEBUGPRIV"
	]

	java_audit_str = ""

	java_audit_str += "".center(OUTPUT_WITH, "=") + "\n"
	java_audit_str += " JAVA VM Audit ".center(OUTPUT_WITH, "=") + "\n"
	java_audit_str += "".center(OUTPUT_WITH, "=") + "\n"

	java_options = dba_registry_df[dba_registry_df["COMP_NAME"].str.lower().str.contains("JAVA Virtual Machine".lower())].to_dict(orient="index")
	java_versions = [ java["COMP_NAME"] + f"[{java['VERSION']}]" for java in java_options.values() ]
	if len(java_versions) > 0:
		java_audit_str += f"[+] Java VM found:" + "\n"
		for java_version in java_versions:
			java_audit_str += f"\t{java_version}" + "\n"
		
		java_audit_str += "\n"

		javaroles_by_users = find_roles_users(dangerous_java_roles, roles_df)
		java_audit_str += f"[-] Number of users that can execute commands via java: {len(javaroles_by_users)}" + "\n"
		if len(javaroles_by_users) > 0:
			java_users_df = pd.DataFrame.from_dict( {"username": list(javaroles_by_users.keys()), "roles": list(javaroles_by_users.values())} )
			java_audit_str += "\n"
			java_audit_str += java_users_df.to_string() + "\n"
			java_audit_str += "\n"
			java_users_df.to_excel(f"{outfolder}/JavaAudit.xlsx")
	
	print(java_audit_str)

	with open(outfolder+"/DB_JavaVMs.txt", "w") as f:
		f.write(java_audit_str)

	
	# ===============================
	# Parameters check
	# ===============================

	parameters_str = ""

	parameters_str += "".center(OUTPUT_WITH, "=") + "\n"
	parameters_str += " Parameters Audit ".center(OUTPUT_WITH, "=") + "\n"
	parameters_str += "".center(OUTPUT_WITH, "=") + "\n"

	parameters_str += "\n"
 
	parameters_check_df = parameters_df[parameters_df["NAME"].isin(["O7_DICTIONARY_ACCESSIBILITY", "remote_os_authent", "remote_os_role"])]
	parameters_check_dict = parameters_check_df.to_dict(orient="index")
	parameters_str += f"Missconfigurated Parameters: {len(parameters_check_df[parameters_check_df['VALUE'] != True])}" + "\n"
	
	for dictionary in parameters_check_dict.values():
		name = dictionary["NAME"]
		value = dictionary["VALUE"]
		parameters_str += f"{name}\tvalue:{value}\t({'OK' if value == True else 'Not OK. Should be True'})" + "\n"
	
	parameters_check_df.to_excel(f"{outfolder}/Parameters.xlsx")

	print(parameters_str)

	with open(outfolder+"/DB_Parameters.txt", "w") as f:
		f.write(parameters_str)

	# ===============================
	# Audit Trails
	# ===============================
 
	audit_trails_str = ""

	audit_trails_str += "".center(OUTPUT_WITH, "=") + "\n"
	audit_trails_str += " Audit Trails ".center(OUTPUT_WITH, "=") + "\n"
	audit_trails_str += "".center(OUTPUT_WITH, "=") + "\n"

	audit_trails_str += "\n"

	audit_parameters_check_df = parameters_df[parameters_df["NAME"].isin(["audit_sys_operations", "audit_trail"])]
	audit_parameters_check_dict = audit_parameters_check_df.to_dict(orient="index")

	audit_trails_str += f"Missconfigurated Audit Parameters: {len(audit_parameters_check_df[audit_parameters_check_df['VALUE'] != True])}" + "\n"
	
	values_audit_functions = {
		'audit_sys_operations': lambda value: "OK" if value == True else "Not OK. Should be True.",
		'audit_trail': lambda value: "OK" if value.split(",")[0].strip() in ("DB", "OS") else "Not OK. Should be DB or OS"
	}

	for dictionary in audit_parameters_check_dict.values():
		name = dictionary["NAME"]
		value = dictionary["VALUE"]
		audit_trails_str += f"{name}\tvalue:{value}\t({values_audit_functions[name](value)})" + "\n"

	print(audit_trails_str)

	with open(outfolder+"/DB_AuditTrails.txt", "w") as f:
		f.write(audit_trails_str)

	# Current system privileges being audited across the system and by user;

	# Check current system auditing options across the system and the user;



if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Process some files.')
	parser.add_argument("-dbv", "--database-version", type=str, help='Specify Oracle DB version (10g, 11g, 12c, 19c).', required=True)
	parser.add_argument("-f", "--folder-path", type=str, help='Path to the folder containing .txt files', required=True)
	parser.add_argument("-o", "--out-folder-path", type=str, help='Path to the folder containing .txt files')
	parser.add_argument('-v', '--verbose', help="Verbosity Level. (-v to -vvv)", action='count', default=0)
	args = parser.parse_args()

	if args.database_version not in ("10g", "11g", "12c", "19c"):
		print(f"Error: {args.database_version} is not a valid Oracle DB version (10g, 11g, 12c, 19c).")
		exit()

	out_folder_path = args.out_folder_path if args.out_folder_path else args.folder_path+"-Audit"
	
	if not os.path.exists(out_folder_path):
		os.makedirs(out_folder_path)

	files_to_copy = {
		"pass_policy_function.txt": "pass_policy_function.txt"
	}
	for src,dst in files_to_copy.items():
		shutil.copy(args.folder_path+"/"+src, out_folder_path+"/"+dst)

	dataframes = generate_dataframes(args.folder_path, set(files_to_copy.keys()))

	audit_data(dataframes, out_folder_path)
