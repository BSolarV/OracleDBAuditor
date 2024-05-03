set echo off
set wrap off
set feedback off
set sqlprompt ''
set trimspool on
set headsep off
set linesize 10000 pagesize 50000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

spool $FILENAME

var v_verify_function VARCHAR2(100);
BEGIN
  SELECT limit INTO :v_verify_function
  FROM dba_profiles
  WHERE profile = 'DEFAULT'
  AND resource_name = 'PASSWORD_VERIFY_FUNCTION';

  CASE :v_verify_function WHEN NULL THEN
  EXECUTE IMMEDIATE 'SELECT dbms_metadata.get_ddl(''FUNCTION'',''' |verbar||verbar| :v_verify_function |verbar||verbar| ''') FROM dual;';
  ELSE
  dbms_output.put_line('No password function found.');
  END CASE;
END;
/

spool off

quit
