set wrap off
set linesize 500 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

select COMP_ID, COMP_NAME, VERSION from dba_registry;

quit
