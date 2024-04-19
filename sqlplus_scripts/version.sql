set wrap off
set linesize 500 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID


prompt Version;
SELECT * FROM V$VERSION; 

prompt "=========================="
prompt Installed Patches;
SELECT action_time, action, namespace, version, comments FROM dba_registry_history;

quit
