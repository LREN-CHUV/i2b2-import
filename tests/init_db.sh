#!/usr/bin/env bash

cd db
alembic upgrade head
cd ..
