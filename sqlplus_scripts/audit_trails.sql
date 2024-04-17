set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

prompt Audit settings ("Audit_trail" should be set to "OS" or "DB" and "audit_sys_operations" should be set to "TRUE");
show parameter audit;

prompt Current system privileges being audited across the system and by user;
SELECT * FROM sys.dba_stmt_audit_opts; 

prompt Check current system auditing options across the system and the user;
SELECT * FROM sys.dba_obj_audit_opts; 

quit