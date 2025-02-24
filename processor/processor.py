import os
import pandas as pd
from sqlalchemy import MetaData

from .models import File
from .db_manager import DatabaseManager


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
