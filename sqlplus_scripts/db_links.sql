set wrap off
set pagesize 1000

connect $USERNAME/$PASS@$HOST:$PORT/$SID

prompt Available links for user;
SELECT * FROM USER_DB_LINKS;
prompt Every link;
SELECT * FROM DBA_DB_LINKS;
prompt Every PUBLIC link;
SELECT * FROM ALL_DB_LINKS;

quit