import os
from django.conf import settings
from django.utils.translation import gettext as _
import pandas as pd
from sqlalchemy import create_engine, MetaData
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

    def convert(self):
        if self.is_processed:
            return
        engine = DatabaseManager.get_engine(self.file)
        file_name = self.file.get_full_path()
        xls = pd.ExcelFile(file_name)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_name, sheet_name=sheet_name)
            df.to_sql(sheet_name, con=engine, if_exists="replace", index=False)

        self.is_processed = True


class DBStructure:
    def __init__(self, file: File):
        self.file = file
        self.engine = DatabaseManager.get_engine(self.file)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

    def fetch(self):
        serialized = []
        for table_name, table in self.metadata.tables.items():
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

    def get_columns(self, table_name: str):
        for table in self.metadata.tables:
            if table.name == table_name:
                return table.columns
