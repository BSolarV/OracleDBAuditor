set wrap off
set serveroutput on size 30000;
set linesize 5000 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

var v_verify_function VARCHAR2(100);
BEGIN
  SELECT limit INTO :v_verify_function
  FROM dba_profiles
  WHERE profile = 'DEFAULT'
  AND resource_name = 'PASSWORD_VERIFY_FUNCTION';

  CASE :v_verify_function WHEN NULL THEN
  EXECUTE IMMEDIATE 'SELECT dbms_metadata.get_ddl(''FUNCTION'',''' || :v_verify_function || ''') FROM dual;';
  ELSE
  dbms_output.put_line('No password function found.');
  END CASE;
END;
/

quit