set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT username, password FROM dba_users WHERE password='EXTERNAL';

quit
