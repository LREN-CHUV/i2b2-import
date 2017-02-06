#!/usr/bin/env bash

cp data-catalog-db/data_catalog_schema.py test_db/
cp db/i2b2_schema.py test_db/

mkdir -p test_db/db_migrations/versions

cd test_db
alembic upgrade head
alembic revision --autogenerate -m "test"
alembic upgrade head
cd ..
