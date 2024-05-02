set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM v$parameter WHERE name='remote_os_roles' OR name='remote_os_authent' OR name='os_authent_prefix' OR name='ldap_directory_access' OR name='ldap_directory_sysauth';

quit
