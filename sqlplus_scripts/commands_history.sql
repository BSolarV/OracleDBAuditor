set wrap off
set linesize 5000 pagesize 10000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT s.SQL_TEXT AS QUERY_TEXT,
       s.SQLTYPE AS SQLTYPE,
       s.ACTION AS ACTION,
       s.PARSING_SCHEMA_NAME AS PARSING_SCHEMA_NAME,
       s.SERVICE AS SERVICE,
       s.COMMAND_TYPE AS COMMAND_TYPE,
       s.ROWS_PROCESSED AS ROWS_PROCESSED,
       s.DISK_READS AS DISK_READS,
       s.FIRST_LOAD_TIME AS FIRST_LOAD_TIME,
       s.LAST_ACTIVE_TIME AS EXECUTION_TIME,
       u.USERNAME AS USER_NAME
FROM V$SQL s
JOIN dba_users u ON s.PARSING_USER_ID = u.USER_ID
WHERE s.LAST_ACTIVE_TIME >= SYSDATE - INTERVAL '3' MONTH
ORDER BY s.LAST_ACTIVE_TIME DESC;

spool off

quit
