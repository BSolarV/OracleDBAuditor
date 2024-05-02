set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

show parameter audit;

quit
