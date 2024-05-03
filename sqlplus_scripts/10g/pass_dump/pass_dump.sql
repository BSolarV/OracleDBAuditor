set echo off
set wrap off
set colsep '|'
set feedback off
set sqlprompt ''
set trimspool on
set headsep off
set linesize 10000 pagesize 50000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

spool $FILENAME

SELECT username,password,account_status FROM dba_users;

spool off

quit
