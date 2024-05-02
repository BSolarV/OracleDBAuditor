set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT action_time, action, namespace, version, comments FROM dba_registry_history;

spool off

quit
