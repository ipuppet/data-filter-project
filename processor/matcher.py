from datetime import datetime
import pandas as pd
from django.conf import settings
from django.utils.translation import gettext as _
from sqlalchemy import MetaData, select, Table, text
from processor.sql_builder import SQLBuilder
from processor.processor import DatabaseManager, FileConverter
from rules.models import Rule

from .models import File


class Matcher:
    def __init__(self):
        self.engine = None
        self.file = None
        self.rule = None
        self.table: Table | None = None
        self.df = None
        self.url_path = ""

    def set_file(self, file: File):
        self.file = file
        FileConverter(self.file).convert()  # Convert the file to SQLite
        self.engine = DatabaseManager.get_engine(self.file)
        return self

    def set_rule(self, rule_id: int):
        self.rule = Rule.objects.get(id=rule_id)
        return self

    def set_table(self, table_name):
        self.table = Table(table_name, MetaData(), autoload_with=self.engine)
        return self

    @property
    def excel_path(self):
        return f"{self.file.get_full_path()}_{self.table.name}.xlsx"

    def fetch(self):
        if self.table is None:
            raise ValueError(_("Table name is not set"))
        session = DatabaseManager.get_session(self.file)

        try:
            sql_builder = SQLBuilder(self.rule, self.table)
            sql, params = sql_builder.build()
            print(sql)
            print(params)

            query = text(sql).execution_options(render_postcompile=True)
            result = session.execute(query, params)
            rows = result.fetchall()
            columns = result.keys()
            self.df = pd.DataFrame(rows, columns=columns)
            self.df.to_excel(self.excel_path, index=False, engine="openpyxl")
        finally:
            session.close()

        self.url_path = self.excel_path.replace(str(settings.MEDIA_ROOT), "")
        self.url_path = self.url_path.replace("\\", "/")
        if self.url_path[0] == "/":
            self.url_path = self.url_path[1:]
        self.url_path = str(settings.MEDIA_URL) + self.url_path
