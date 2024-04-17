set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

select * from DBA_AUDIT_POLICY;

quit