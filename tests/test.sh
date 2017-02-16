#!/usr/bin/env bash

echo "Starting DB container..."
db_docker_id_1=$(docker run -d -p 5433:5432 postgres)
db_docker_id_2=$(docker run -d -p 5434:5432 postgres)
sleep 3  # TODO: replace this by a test

echo "Searching for gateway IP..."
GATEWAY_IP=$(ip addr | grep docker | grep inet | grep -Eo '[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*')

echo "Creating deploying schemas..."
docker run --rm -e "DB_URL=postgresql://postgres:postgres@$GATEWAY_IP:5433/postgres" hbpmip/data-catalog-setup:1.3.1 upgrade head
docker run --rm -e "DB_URL=postgresql://postgres:postgres@$GATEWAY_IP:5434/postgres" hbpmip/i2b2-setup:1.3.1 upgrade head
# c0692da
sleep 5  # TODO: replace this by a test

echo "Running unit tests..."
nosetests unittest.py
ret=$?

# Remove DB container (if not on CircleCI)
if [ -z "$CIRCLECI" ] || [ "$CIRCLECI" = false ] ; then
    echo "Removing DB container..."
    docker rm -f ${db_docker_id_1}
    docker rm -f ${db_docker_id_2}
fi

exit "$ret"
