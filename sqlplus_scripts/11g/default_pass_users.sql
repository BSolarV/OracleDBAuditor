set wrap off
set linesize 500 linesize 1000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * from dba_users_with_defpwd ORDER BY username;

quit
