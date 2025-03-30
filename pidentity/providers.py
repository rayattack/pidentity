from typing import TYPE_CHECKING
from asyncpg import connect


if TYPE_CHECKING: from pidentity.control import Control


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


class PostgresEngine():
    async def __init__(self, dsn):
        self.__pool = None

    @property
    def cursor(self):
        return self.__pool

    async def _init(self):
        sql = '''
            create schema if not exists c5;
            CREATE TABLE IF NOT EXISTS c5.contracts (
                domain text NOT NULL,
                upon text NOT NULL,
                unto text NOT NULL,
                PRIMARY KEY (domain, upon, unto)
            );

            CREATE TABLE IF NOT EXISTS c5.conditions (
                domain text NOT NULL,
                upon text NOT NULL,
                unto text NOT NULL,
                what text NOT NULL CHECK(what in ('context', 'content', 'contact')),
                condition JSON NOT NULL,
                metadata JSON,
                timestamped timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(domain, upon, unto, what),
                FOREIGN KEY(domain, upon, unto) references c5.contracts(domain, upon, unto)
            );
        '''
        await self.pool.execute(sql)

    async def _save(self) -> 'Control':
        async with self.__pool.acquire() as cursor:
            try: cursor.executemany(UPSERT_CONDITIONS_SQL, self._unsaved)
            except IndexError: pass
            finally:
                cursor.close()
                cursor.connection.commit()

        self._saved = self._unsaved
        self._unsaved = []
        return self
    
    async def _swap(self) -> 'Control':
        cursor = self.cursor
        try: cursor.executemany(UPDATE_CONDITIONS_SQL, self._unswapped)
        except: pass
        finally: cursor.close(); cursor.connection.commit()
        return self

    async def _sync(self, values: list):
        # TODO: this should be unsync not sync
        # if db file exists - nuke it
        if not self._db: raise ValueError('Database not yet initialised')
        cursor = self._db.cursor()
        cursor.executemany(INSERT_CONDITIONS_SQL, values)

    async def select(self, on: str, to: str, at: str, domain = '*'):
        cursor = self.cursor
        condition = ''
        try:  condition = cursor.execute(SELECT_CONDITIONS_SQL, {ON: on, TO: to, AT: at, DOMAIN: domain}).fetchone()
        except: pass
        finally: cursor.close()
        if condition: return loads(condition[0])


class SqliteProvider(object):
    pass
