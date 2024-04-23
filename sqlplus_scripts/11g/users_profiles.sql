set wrap off
set linesize 500 linesize 1000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM dba_profiles order by profile;

quit
