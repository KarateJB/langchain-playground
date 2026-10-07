#!/usr/bin/env bash

# Create a new database
psql -U $POSTGRES_USER -f /docker-entrypoint-initdb.d/create_db.sql

# Create extensions if not exist
psql -U $POSTGRES_USER -d $POSTGRES_DB -f /docker-entrypoint-initdb.d/create_extensions.sql
echo
