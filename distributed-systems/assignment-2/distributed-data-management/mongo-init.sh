#!/bin/bash

set -e

KEYFILE_PATH="/data/keyfile/mongodb-keyfile"

if [ ! -f "$KEYFILE_PATH" ]; then
    echo "Generating keyfile..."
    openssl rand -base64 756 > "$KEYFILE_PATH"
    chmod 400 "$KEYFILE_PATH"
    chown mongodb:mongodb "$KEYFILE_PATH"
fi

if [ ! -f /data/db/.initialized ]; then
    echo "First run - starting MongoDB without auth..."
    mongod --replSet rs0 --bind_ip_all --port 27017 &
    MONGO_PID=$!

    echo "Waiting for MongoDB to start..."
    until mongosh --port 27017 --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
        sleep 1
    done

    echo "MongoDB started. Initializing replica set..."
    mongosh --port 27017 <<EOF
rs.initiate({
    _id: 'rs0',
    members: [
        { _id: 0, host: 'mongo1:27017', priority: 2 },
        { _id: 1, host: 'mongo2:27017', priority: 1 },
        { _id: 2, host: 'mongo3:27017', priority: 1 }
    ]
});
EOF

    echo "Waiting for replica set to stabilize..."
    sleep 10

    echo "Creating admin user..."
    mongosh --port 27017 <<EOF
use admin
db.createUser({
    user: 'admin',
    pwd: 'admin123',
    roles: [{ role: 'root', db: 'admin' }]
});
EOF

    echo "Admin user created. Marking as initialized..."
    touch /data/db/.initialized

    echo "Stopping MongoDB..."
    mongosh --port 27017 admin --eval "db.shutdownServer()" || true
    wait $MONGO_PID

    echo "Restarting with authentication..."
fi

exec mongod --replSet rs0 --keyFile "$KEYFILE_PATH" --bind_ip_all --port 27017
