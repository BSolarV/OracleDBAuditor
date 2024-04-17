#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found."
    exit 1
fi

# Load variables from .env file
source .env

# Check if SID is empty
if [ -z "Report-$SID" ]; then
    exit
else
    mkdir -p Report-$SID
fi

# Define a list of SQL files
sql_files=("audit_trails_config" "audit_trails_users_objects" "audit_trails_users_statements" "dba_registry" "dba_users" "db_links" "every_parameter" "last_logon" "network_policies" "pass_policy" "privs" "procedures_privs" "proxy_users" "public_tab_privs" "remote_os_auth" "roles" "users" "version")

for sql_file in "${sql_files[@]}"; do

    echo "Running $sql_file..."

    # Backup original commands.sql file
    cp sqlplus_scripts/$sql_file.sql ${sql_file}_tmp.sql

    # Replace variables in a temporary file
    sed -i "s/\$USERNAME/$USERNAME/g" ${sql_file}_tmp.sql
    sed -i "s/\$PASS/$PASS/g" ${sql_file}_tmp.sql
    sed -i "s/\$HOST/$HOST/g" ${sql_file}_tmp.sql
    sed -i "s/\$PORT/$PORT/g" ${sql_file}_tmp.sql
    sed -i "s/\$SID/$SID/g" ${sql_file}_tmp.sql

    # Execute SQL commands using SQL*Plus
    cat ${sql_file}_tmp.sql | sqlplus -s /nolog > Report-$SID/${sql_file}.txt

    # Clean up temporary files
    rm ${sql_file}_tmp.sql

done
