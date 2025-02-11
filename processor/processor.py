from datetime import datetime
import os
from typing import Dict
from django.conf import settings
from django.utils.translation import gettext as _
import pandas as pd
from sqlalchemy import create_engine, MetaData, select, Table
from sqlalchemy.orm import sessionmaker
from .models import File


class DatabaseManager:
    _instances = {}

    @classmethod
    def get_db_url(cls, file: File):
        return f"sqlite:///{file.get_full_path()}.sqlite"

    @classmethod
    def get_engine(cls, file: File):
        if file.id not in cls._instances:
            cls._instances[file.id] = create_engine(cls.get_db_url(file))
        return cls._instances[file.id]

    @classmethod
    def get_session(cls, file: File):
        engine = cls.get_engine(file)
        Session = sessionmaker(bind=engine)
        return Session()


class FileConverter:
    def __init__(self, file: File):
        self.file = file
        self.sqlite_file = f"{self.file.get_full_path()}.sqlite"
        self.is_processed = os.path.exists(self.sqlite_file)
        self.engine = DatabaseManager.get_engine(self.file)

    def convert(self):
        if self.is_processed:
            return

        file_name = self.file.get_full_path()
        xls = pd.ExcelFile(file_name)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_name, sheet_name=sheet_name)
            df.to_sql(sheet_name, con=self.engine, if_exists="replace", index=False)

        # TODO Test only: Copy the sqlite file to settings.MEDIA_ROOT / test / userdb.sqlite
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "test"), exist_ok=True)
        os.system(
            f"cp {self.file.get_full_path()}.sqlite {settings.MEDIA_ROOT}/test/userdb.sqlite"
        )
        self.is_processed = True


class TableStructure:
    def __init__(self, file: File):
        self.file = file
        self.engine = DatabaseManager.get_engine(self.file)

    def serialize_tables(self, tables: Dict[str, Table]):
        serialized = []
        for table_name, table in tables.items():
            serialized.append(
                {
                    "name": table_name,
                    "columns": [
                        {
                            "name": column.name,
                            "type": str(column.type),
                            "nullable": column.nullable,
                            "primary_key": column.primary_key,
                        }
                        for column in table.columns
                    ],
                }
            )
        return serialized

    def fetch(self):
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return self.serialize_tables(metadata.tables)


class Matcher:
    def __init__(self, file: File):
        self.file = file
        self.engine = DatabaseManager.get_engine(self.file)
        self.rules = []
        self.table = None

    def set_rules(self, rules):
        self.rules = rules
        return self

    def set_table(self, table_name):
        self.table = table_name
        return self

    def _fetch_result(self, result):
        data = []
        for row in result:
            row_data = []
            for value in row:
                if isinstance(value, datetime):
                    row_data.append(value.timestamp())
                else:
                    row_data.append(value)
            data.append(row_data)
        return data

    def fetch_all_data(self, page_number, items_per_page):
        session = DatabaseManager.get_session(self.file)
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        all_tables_data = []

        for table_name, table in metadata.tables.items():
            total_count = session.query(table).count()

            # 分页查询
            query = (
                select(table)
                .offset((page_number - 1) * items_per_page)
                .limit(items_per_page)
            )
            result = session.execute(query)
            all_tables_data.append(
                {
                    "name": table_name,
                    "count": total_count,
                    "columns": list(result.keys()),
                    "data": self._fetch_result(result),
                }
            )

        return all_tables_data

    def fetch(self):
        if not self.table:
            raise ValueError(_("Table name is not set"))
        session = DatabaseManager.get_session(self.file)
        table = Table(self.table, MetaData(), autoload_with=self.engine)

        # TODO: Add support for rules
        query = select(table)

        return self._fetch_result(session.execute(query))
