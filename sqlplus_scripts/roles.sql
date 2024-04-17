set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM dba_role_privs;

quit