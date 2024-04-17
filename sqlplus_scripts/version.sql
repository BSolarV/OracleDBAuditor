set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID


prompt Version;
SELECT * FROM V$VERSION; 

prompt Installed Patches;
SELECT action_time, action, namespace, version, comments FROM dba_registry_history;

quit
