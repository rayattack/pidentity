from typing import TypedDict
from sqlite3 import Cursor


SQL = '''
    CREATE TABLE IF NOT EXISTS contracts (
        upon varchar(32) NOT NULL,
        unto varchar(32) NOT NULL,
        PRIMARY KEY (upon, unto)
    );

    CREATE TABLE IF NOT EXISTS conditions (
        upon varchar(32) NOT NULL,
        unto varchar(32) NOT NULL,
        what varchar(32) NOT NULL CHECK(what in ('context', 'content', 'contact')),
        condition JSON NOT NULL,
        timestamped timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(upon, unto, what),
        FOREIGN KEY(upon, unto) references pidentity_contracts(upon, unto)
    );
'''


INSERT_CONDITIONS_SQL = 'INSERT INTO conditions (upon, unto, what, condition) VALUES (:upon, :unto, :what, :condition);'
DELETE_CONDITIONS_SQL = 'DELETE FROM conditions WHERE upon = :upon AND unto = :unto AND what = :what;'
UPDATE_CONDITIONS_SQL = 'UPDATE conditions SET upon = :upon, unto = :unto, what = :what, conditions := condition;'
SELECT_CONDITIONS_SQL = 'SELECT * FROM conditions WHERE upon = :upon AND unto = :unto AND what = :what;'
