from typing import TypedDict
from sqlite3 import Cursor


SQL = '''
    CREATE TABLE IF NOT EXISTS contracts (
        domain varchar(32) NOT NULL,
        upon varchar(32) NOT NULL,
        unto varchar(32) NOT NULL,
        PRIMARY KEY (domain, upon, unto)
    );

    CREATE TABLE IF NOT EXISTS conditions (
        domain varchar(32) NOT NULL,
        upon varchar(32) NOT NULL,
        unto varchar(32) NOT NULL,
        what varchar(32) NOT NULL CHECK(what in ('context', 'content', 'contact')),
        condition JSON NOT NULL,
        metadata JSON,
        timestamped timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(domain, upon, unto, what),
        FOREIGN KEY(domain, upon, unto) references contracts(domain, upon, unto)
    );
'''


INSERT_CONDITIONS_SQL = 'INSERT INTO conditions (domain, upon, unto, what, condition, metadata) VALUES (:domain, :upon, :unto, :what, :condition, :metadata);'
DELETE_CONDITIONS_SQL = 'DELETE FROM conditions WHERE domain = :domain AND upon = :upon AND unto = :unto AND what = :what;'
UPDATE_CONDITIONS_SQL = 'UPDATE conditions SET conditions := condition and metadata = :metadata WHERE domain = :domain AND upon = :upon AND unto = :unto AND what = :what;'
SELECT_CONDITIONS_SQL = 'SELECT condition FROM conditions WHERE domain = :domain AND upon = :upon AND unto = :unto AND what = :what;'
UPSERT_CONDITIONS_SQL = """
insert into
    conditions(domain, upon, unto, what, condition, metadata)
    values (:domain, :upon, :unto, :what, :condition, :metadata)
on conflict(domain, upon, unto, what)
    do update set condition = :condition
"""
