#!/bin/bash

# Default values
DB_VERSION=""
PASSWORD_HASHES=false
ENV_FILE=".env"

# Help function
function display_help {
    echo "Usage: $0 -dbv DATABASE_VERSION [-p] [-e ENV_FILE] [-h]"
    echo "Options:"
    echo "  -dbv, --database-version    Specify Oracle DB version (10g, 11g, 12c, 19c)."
    echo "  -p, --password-hashes       Retrieve password hashes of users."
    echo "  -e, --env-file              Specify the .env file (default is .env)"
    echo "  -h, --help                  Display this help message."
    exit 0
}

# Function to validate database version
function validate_db_version {
    case "$1" in
        10g|11g|12c|19c)
            ;;
        *)
            echo "Error: Invalid database version. Valid values are '10g', '11g', '12c', '19c'."
            display_help
            ;;
    esac
}

# Function to execute main code
function main {
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        echo "Error: $ENV_FILE file not found."
        exit 1
    fi

    # Load variables from .env file
    source "$ENV_FILE"

    # Check if SID is empty
    if [ -z "Report-$SID" ]; then
        exit
    else
        mkdir -p Report-$SID
    fi

    cd Report-$SID

    # Run scripts for every DB version
    for sql_file_raw in ../sqlplus_scripts/*.sql; do
        
        sql_file_with_path=${sql_file_raw%.*}
        sql_file=${sql_file_with_path##*/}
        echo "Running $sql_file_raw..."
        

        # Backup original commands.sql file
        cp ../sqlplus_scripts/$sql_file.sql ${sql_file}_tmp.sql

        # Replace variables in a temporary file
        sed -i "s/\$FILENAME/${sql_file}.txt/g" ${sql_file}_tmp.sql
        sed -i "s/\$USERNAME/$USERNAME/g" ${sql_file}_tmp.sql
        sed -i "s/\$PASS/$PASS/g" ${sql_file}_tmp.sql
        sed -i "s/\$HOST/$HOST/g" ${sql_file}_tmp.sql
        sed -i "s/\$PORT/$PORT/g" ${sql_file}_tmp.sql
        sed -i "s/\$SID/$SID/g" ${sql_file}_tmp.sql

        # Execute SQL commands using SQL*Plus
        cat ${sql_file}_tmp.sql | sqlplus -s /nolog > /dev/null

        # Clean up temporary files
        rm ${sql_file}_tmp.sql
    done

    # Run scripts specific to a version
    for sql_file_raw in ../sqlplus_scripts/$DB_VERSION/*.sql; do

        sql_file_with_path=${sql_file_raw%.*}
        sql_file=${sql_file_with_path##*/}
        echo "Running $sql_file_raw..."

        # Backup original commands.sql file
        cp ../sqlplus_scripts/$DB_VERSION/$sql_file.sql ${sql_file}_tmp.sql

        # Replace variables in a temporary file
        sed -i "s/\$FILENAME/${sql_file}.txt/g" ${sql_file}_tmp.sql
        sed -i "s/\$USERNAME/$USERNAME/g" ${sql_file}_tmp.sql
        sed -i "s/\$PASS/$PASS/g" ${sql_file}_tmp.sql
        sed -i "s/\$HOST/$HOST/g" ${sql_file}_tmp.sql
        sed -i "s/\$PORT/$PORT/g" ${sql_file}_tmp.sql
        sed -i "s/\$SID/$SID/g" ${sql_file}_tmp.sql

        # Execute SQL commands using SQL*Plus
        cat ${sql_file}_tmp.sql | sqlplus -s /nolog > /dev/null

        # Clean up temporary files
        rm ${sql_file}_tmp.sql
    done

    # Check and run password hashes dump
    if [ $PASSWORD_HASHES ]; then
        for sql_file_raw in ../sqlplus_scripts/$DB_VERSION/pass_dump/*.sql; do
            
            sql_file_with_path=${sql_file_raw%.*}
	    sql_file=${sql_file_with_path##*/}
            echo "Running $sql_file_raw..."

            # Backup original commands.sql file
            cp ../sqlplus_scripts/$DB_VERSION/pass_dump/$sql_file.sql ${sql_file}_tmp.sql

            # Replace variables in a temporary file
            sed -i "s/\$FILENAME/${sql_file}.txt/g" ${sql_file}_tmp.sql
            sed -i "s/\$USERNAME/$USERNAME/g" ${sql_file}_tmp.sql
            sed -i "s/\$PASS/$PASS/g" ${sql_file}_tmp.sql
            sed -i "s/\$HOST/$HOST/g" ${sql_file}_tmp.sql
            sed -i "s/\$PORT/$PORT/g" ${sql_file}_tmp.sql
            sed -i "s/\$SID/$SID/g" ${sql_file}_tmp.sql

            # Execute SQL commands using SQL*Plus
            cat ${sql_file}_tmp.sql | sqlplus -s /nolog > /dev/null

            # Clean up temporary files
            rm ${sql_file}_tmp.sql
        done
    fi
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -dbv|--database-version)
            validate_db_version "$2"
            DB_VERSION="$2"
            shift 2
            ;;
        -p|--password-hashes)
            PASSWORD_HASHES=true
            shift
            ;;
        -e|--env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        -h|--help)
            display_help
            ;;
        *)
            echo "Error: Invalid argument $1"
            display_help
            ;;
    esac
done

# Check if -dbv parameter is provided
if [ -z "$DB_VERSION" ]; then
    echo "Error: -dbv parameter is required."
    display_help
fi

# Execute main code
main
