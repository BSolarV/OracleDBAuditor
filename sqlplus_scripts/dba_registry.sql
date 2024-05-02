set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

select COMP_ID, COMP_NAME, VERSION from dba_registry;

spool off

quit
