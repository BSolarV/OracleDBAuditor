set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM sys.dba_obj_audit_opts; 

quit