#!/usr/bin/env bash

# Start DB container
echo "Starting DB container..."
db_docker_id_1=$(docker run -d -p 5433:5432 hbpmip/data-catalog-db)
db_docker_id_2=$(docker run -d -p 5434:5432 hbpmip/i2b2-db)

# Wait for DB to be ready
echo "Waiting for DB to be ready..."
sleep 10  # TODO: replace this by a test

# Run unit tests
echo "Running unit tests..."
nosetests unittest.py
ret=$?

# Remove DB container (if not on CircleCI)
if [ -z "$CIRCLECI" ] || [ "$CIRCLECI" = false ] ; then
    echo "Removing DB container..."
    docker kill ${db_docker_id_1}
    docker kill ${db_docker_id_2}
    docker rm -f ${db_docker_id_1}
    docker rm -f ${db_docker_id_2}
fi

exit "$ret"
