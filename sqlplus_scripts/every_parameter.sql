set echo off
set wrap off
set colsep '|'
set feedback off
set sqlprompt ''
set trimspool on
set headsep off
set linesize 10000 pagesize 999999

connect $USERNAME/$PASS@$HOST:$PORT/$SID

spool $FILENAME

SELECT * FROM v$parameter; 

spool off

quit
