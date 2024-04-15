set wrap off
set linesize 500 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT * FROM dba_tab_privs WHERE table_name='UTL_FILE' OR table_name='UTL_HTTP' OR table_name='UTL_SMTP' OR table_name='UTL_TCP' OR table_name='DBMS_JAVA' OR table_name='DBMS_JOB' OR table_name='DBMS_SQL'OR table_name='DBMS_SCHEDULER' OR table_name='DBMS_ADVISOR' OR table_name='DBMS_XSLPROCESSOR' OR table_name='DBMS_LOB' OR table_name='DBMS_OBFUSCATION_TOOLKIT' OR table_name='OWA_UTIL';

quit