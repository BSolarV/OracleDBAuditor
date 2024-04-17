set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

select username, max(logon_time) as logon_time from v$session where username is not null group by username;

quit