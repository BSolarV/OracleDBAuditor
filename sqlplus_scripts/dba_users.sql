set wrap off
set linesize 500 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM v$pwfile_users;

quit