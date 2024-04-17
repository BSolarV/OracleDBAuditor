set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM v$parameter; 

quit
