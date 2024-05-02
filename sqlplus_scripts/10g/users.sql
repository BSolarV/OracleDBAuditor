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

SELECT USERNAME, USER_ID, ACCOUNT_STATUS, LOCK_DATE, EXPIRY_DATE, DEFAULT_TABLESPACE, TEMPORARY_TABLESPACE, CREATED, PROFILE, EXTERNAL_NAME FROM dba_users;

spool off

quit
