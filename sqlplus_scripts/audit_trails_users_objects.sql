set wrap off
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM sys.dba_obj_audit_opts; 

spool off

quit
