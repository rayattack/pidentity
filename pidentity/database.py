from typing import TypedDict
from sqlite3 import Cursor


SQL = '''
    CREATE TABLE IF NOT EXISTS contracts (
        upon varchar(32) NOT NULL,
        unto varchar(32) NOT NULL,
        PRIMARY KEY (upon, unto)
    );

    CREATE TABLE IF NOT EXISTS regulators (
        upon varchar(32) NOT NULL,
        unto varchar(32) NOT NULL,
        what varchar(32) NOT NULL CHECK(what in ('context', 'content', 'contact')),
        conditions JSON NOT NULL,
        timestamped timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(upon, unto, what),
        FOREIGN KEY(upon, unto) references pidentity_contracts(upon, unto)
    );
'''


INSERT_REGULATORS_SQL = 'INSERT INTO regulators (upon, unto, what, conditions) VALUES (:upon, :unto, :what, :conditions);'
DELETE_REGULATORS_SQL = 'DELETE FROM regulators WHERE upon = :upon AND unto = :unto AND what = :what;'
UPDATE_REGULATORS_SQL = 'UPDATE regulators SET upon = :upon, unto = :unto, what = :what, conditions := conditions;'


def initdb(cursor: Cursor):
    cursor.executescript(SQL)


async def initialize_sql(connection):
    sql = '''
        CREATE SCHEMA IF NOT EXISTS pidentity;

        CREATE TABLE IF NOT EXISTS contracts (
            upon varchar(32) NOT NULL,
            unto varchar(32) NOT NULL,
            PRIMARY KEY (upon, unto)
        );

        CREATE TABLE IF NOT EXISTS regulators (
            upon varchar(32) NOT NULL,
            unto varchar(32) NOT NULL,
            what JSON NOT NULL,
            what varchar(32) NOT NULL CHECK(what in ('context', 'content', 'contact')),
            timestamped timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(upon, unto) references contracts(upon, unto)
        );
    '''
    await connection.execute(sql)


def get_contracts(cursor: Cursor, upon: str, unto: str):
    sql = 'SELECT * FROM pidentity.regulators WHERE upon = ? AND unto = ?;'
    return cursor.execute(sql, (upon, unto))


async def add_contracts(connection, upon: str, unto: str, contracts):
    contact = contracts.get('contact', {})
    content = contracts.get('content', {})
    context = contracts.get('context', {})
    sql = 'INSERT INTO pidentity.regulators (upon, unto, what, conditions) VALUES ($1, $2, $3, $4);'
    return await connection.executemany(sql, [
        (upon, unto, 'contact', contact),
        (upon, unto, 'content', content),
        (upon, unto, 'context', context)
    ])
