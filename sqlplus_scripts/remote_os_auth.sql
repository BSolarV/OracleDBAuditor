set wrap off
set linesize 500 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID


prompt Listing relevant parameters;
SELECT * FROM v$parameter WHERE name='remote_os_roles' OR name='remote_os_authent' OR name='os_authent_prefix' OR	name='ldap_directory_access' OR name='ldap_directory_sysauth';

prompt Listing possible users;
SELECT username, password FROM dba_users WHERE password='EXTERNAL';

quit
