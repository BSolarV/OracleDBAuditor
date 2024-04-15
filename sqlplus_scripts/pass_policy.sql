set wrap off
set linesize 500 pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

SELECT resource_name,limit from dba_profiles where profile='DEFAULT';

prompt ""
prompt Password verify function
DECLARE
  v_verify_function VARCHAR2(100);
  v_ddl_query VARCHAR2(200);
BEGIN
  -- Recuperar el valor de PASSWORD_VERIFY_FUNCTION
  SELECT PASSWORD_VERIFY_FUNCTION INTO v_verify_function
  FROM dba_profiles
  WHERE profile = 'DEFAULT'
  AND resource_name = 'PASSWORD_VERIFY_FUNCTION';

  -- Verificar si el valor no es NULL y ejecutar la consulta adicional
  IF v_verify_function IS NOT NULL THEN
	v_ddl_query := 'select dbms_metadata.get_ddl(''FUNCTION'',''' || v_verify_function || ''') from dual;';
	EXECUTE IMMEDIATE v_ddl_query;
  ELSE
	DBMS_OUTPUT.PUT_LINE('No password verify found.');
  END IF;
END;
/

quit