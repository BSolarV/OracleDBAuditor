set echo off
set wrap off
set colsep '|verbar|'
set feedback off
set sqlprompt ''
set trimspool on
set headsep off
set linesize 10000 pagesize 50000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

spool $FILENAME

SELECT * from dba_users_with_defpwd ORDER BY username;

spool off

quit
