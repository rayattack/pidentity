

from typing import TypedDict


async def initialize_sql(connection):
    sql = '''
        CREATE SCHEMA IF NOT EXISTS pydentity;

        CREATE TABLE IF NOT EXISTS pydentity.contracts (
            activity varchar(32) NOT NULL,
            towards varchar(32) NOT NULL,
            PRIMARY KEY (activity, towards)
        );

        CREATE TABLE IF NOT EXISTS pydentity.regulators (
            activity varchar(32) NOT NULL,
            towards varchar(32) NOT NULL,
            content JSON NOT NULL,
            regulates varchar(32) NOT NULL CHECK(regulates in ('context', 'content', 'contact')),
            timestamped timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(activity, towards) references pydentity_contracts(activity, towards)
        );
    '''
    await connection.execute(sql)


async def get_contracts(connection, activity: str, towards: str):
    sql = 'SELECT * FROM pydentity.regulators WHERE activity = $1 AND towards = $2;'
    return await connection.fetch(sql, activity, towards)


async def add_contracts(connection, activity: str, towards: str, contracts):
    contact = contracts.get('contact', {})
    content = contracts.get('content', {})
    context = contracts.get('context', {})
    sql = 'INSERT INTO pydentity.regulators (activity, towards, content, regulates) VALUES ($1, $2, $3, $4);'
    return await connection.executemany(sql, [
        (activity, towards, content, 'contact', contact),
        (activity, towards, content, 'content', content),
        (activity, towards, content, 'context', context)
    ])
