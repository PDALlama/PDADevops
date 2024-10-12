#!/bin/bash

echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
service ssh start
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

if [ ! -s "/var/lib/postgresql/data/PG_VERSION" ]; then

(echo $POSTGRES_PASSWORD; echo $POSTGRES_PASSWORD) | passwd postgres

su postgres -c "initdb -D /var/lib/postgresql/data"
su postgres -c "pg_ctl -D /var/lib/postgresql/data start"
su postgres -c "createdb $POSTGRES_DB"

echo "host replication repl_user 0.0.0.0/0 md5" >> "/var/lib/postgresql/data/pg_hba.conf"
echo "host db_bot_tg postgres 0.0.0.0/0 md5" >> "/var/lib/postgresql/data/pg_hba.conf"

cat >> /var/lib/postgresql/data/postgresql.conf <<EOF

wal_level = replica
archive_mode = on
archive_command = 'cd .'

max_wal_senders = 10
wal_log_hints = on

logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql.log'
log_line_prefix = '%m [%p] %q%u@%d '
log_replication_commands = on

EOF

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

ALTER USER $POSTGRES_USER PASSWORD '$POSTGRES_PASSWORD';

CREATE USER $POSTGRES_REPLICATION_USER REPLICATION LOGIN CONNECTION LIMIT 100 ENCRYPTED PASSWORD '$POSTGRES_REPLICATION_PASSWORD';

CREATE TABLE emails(
    ID SERIAL PRIMARY KEY,
    email VARCHAR (100) NOT NULL
);

CREATE TABLE phone_numbers(
    ID SERIAL PRIMARY KEY,
    number VARCHAR (50) NOT NULL
);

INSERT INTO emails(email)
VALUES ('test1@mail.ru'),
        ('test2@gmail.com'),
        ('test3@yandex.ru'),
        ('test4@ya.ru');

INSERT INTO phone_numbers(number)

VALUES ('88005550000'),
        ('8-800-555-00-00'),
        ('8(800) 555 00 00'),
        ('+7(800)5550000');

EOSQL

fi

su postgres -c "pg_ctl stop"

exec "$@"