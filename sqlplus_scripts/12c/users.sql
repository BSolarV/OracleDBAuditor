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

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT USERNAME, USER_ID, ACCOUNT_STATUS, LOCK_DATE, EXPIRY_DATE, PROFILE, password_versions, DEFAULT_TABLESPACE, TEMPORARY_TABLESPACE, CREATED, PROFILE, EXTERNAL_NAME FROM dba_users;

spool off

quit
