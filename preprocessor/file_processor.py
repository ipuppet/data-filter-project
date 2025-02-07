from datetime import datetime
import os
from django.conf import settings
import pandas as pd
from sqlalchemy import Engine, create_engine
from .models import File


class FileProcessor:
    def __init__(self, file: File):
        self.file = file

    def sqlite_file_path(self) -> Engine:
        today = datetime.today().strftime("%Y/%m/%d")
        sqlite_file_name = f"{self.file.id}.sqlite"
        sqlite_file_path = os.path.join(
            settings.MEDIA_ROOT, "databases", today, sqlite_file_name
        )
        os.makedirs(os.path.dirname(sqlite_file_path), exist_ok=True)

        return sqlite_file_path

    def process(self):
        file_name = self.file.get_full_path()
        xls = pd.ExcelFile(file_name)
        sqlite_file_path = self.sqlite_file_path()
        engine = create_engine(f"sqlite:///{sqlite_file_path}")
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_name, sheet_name=sheet_name)
            df.to_sql(sheet_name, con=engine, if_exists="replace", index=False)

        # TODO Test only: Copy the sqlite file to settings.MEDIA_ROOT / test / userdb.sqlite
        os.makedirs(os.path.join(settings.MEDIA_ROOT, "test"), exist_ok=True)
        os.system(f"cp {sqlite_file_path} {settings.MEDIA_ROOT}/test/userdb.sqlite")
