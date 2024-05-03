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

select username, max(logon_time) as logon_time from v$session where username is not null group by username;

spool off

quit
