#!/bin/bash

if [ ! -s "/var/lib/postgresql/data/PG_VERSION" ]; then

echo "*:*:*:$POSTGRES_REPL_USER:$POSTGRES_REPL_PASSWORD" > /var/lib/postgresql/.pgpass

chown postgres:postgres /var/lib/postgresql/.pgpass
chmod 0600 /var/lib/postgresql/.pgpass

su postgres << BASH
  whoami;
  pwd;
BASH

#chown postgres:postgres /var/lib/postgresql/.pgpass
#chmod 0666 /var/lib/postgresql/.pgpass

echo "waiting"
su postgres << BASH
until pg_basebackup -R -h ${POSTGRES_MASTER_HOST} -D /var/lib/postgresql/data -U ${POSTGRES_REPL_USER} -P -w
    do
        echo "Waiting for master to connect..."
        sleep 1s
done
BASH

echo "connected"

set -e

echo "host replication all 0.0.0.0/0 md5" >> "/var/lib/postgresql/data/pg_hba.conf"

chown postgres:postgres /var/lib/postgresql/data -R
chmod 700 /var/lib/postgresql/data -R

fi

sed -i 's/wal_level = hot_standby/wal_level = replica/g' /var/lib/postgresql/data/postgresql.conf

# .pgpass somehow deletes after this manipulations

echo "*:*:*:$POSTGRES_REPL_USER:$POSTGRES_REPL_PASSWORD" > /var/lib/postgresql/.pgpass

chown postgres:postgres /var/lib/postgresql/.pgpass
chmod 0600 /var/lib/postgresql/.pgpass

exec "$@"