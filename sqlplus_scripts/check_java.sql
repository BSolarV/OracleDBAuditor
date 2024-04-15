set wrap off
set linesize 500 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

select comp_name, version from dba_registry where comp_name like '%JAVA%';

quit