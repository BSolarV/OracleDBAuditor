set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

select * from dba_registry;

quit