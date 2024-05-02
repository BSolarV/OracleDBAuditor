set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT resource_name,limit from dba_profiles where profile='DEFAULT';

spool off

quit
