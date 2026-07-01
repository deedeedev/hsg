import csv
from os import sep
import sqlalchemy as sql

from sqlalchemy import Table, Column, Integer, String, MetaData
from utils.constants import TATOEBA_CSV, TATOEBA_DB
from typing import Union

class TatoebaSqlite:

    ZH_EN = 'zh_en'

    def __init__(self):
        self.create_db()
    
    def create_db(self):
        self.db_engine = sql.create_engine(f'sqlite:///{TATOEBA_DB}', echo=True)
    
    def create_db_tables(self):
        metadata = MetaData()
        zh_en = Table(
                self.ZH_EN,
                metadata,
                Column('id', Integer, primary_key=True),
                Column('sentence_id', Integer),
                Column('hanzi', String),
                Column('base_id', Integer),
                Column('translation', String),
            )
        try:
            metadata.create_all(self.db_engine)
            print('Tables created')
        except Exception as e:
            print('Error occurred during table creation.')
            print(e)
    
    def populate_db(self) -> None:
        with open(TATOEBA_CSV) as f:
            reader = csv.reader(f, delimiter="\t")
            for row in reader:
                sentence_id, hanzi, base_id, translation = row
                stmt = sql.insert(self.ZH_EN).values(sentence_id=sentence_id, hanzi=hanzi, base_id=base_id, translation=translation)
                with self.db_engine.connect() as conn:
                    conn.execute(stmt)
                    conn.commit()

if __name__ == '__main__':
    tsql = TatoebaSqlite()
    tsql.create_db()
    tsql.create_db_tables()
    tsql.populate_db()