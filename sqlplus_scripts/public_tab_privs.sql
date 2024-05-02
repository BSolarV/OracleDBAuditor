set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT table_name, privilege FROM sys.dba_tab_privs WHERE grantee='PUBLIC';

quit
