set echo off
set wrap off
set colsep '|verbar|'
set feedback off
set sqlprompt ''
set trimspool on
set headsep off
set linesize 10000 pagesize 50000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

spool $FILENAME

SELECT * FROM v$parameter WHERE name='remote_os_roles' OR name='remote_os_authent' OR name='os_authent_prefix' OR name='ldap_directory_access' OR name='ldap_directory_sysauth';

spool off

quit
