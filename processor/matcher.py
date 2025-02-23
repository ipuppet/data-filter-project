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
        self.table_name: str = ""

    def set_file(self, file: File):
        self.file = file
        FileConverter(self.file).convert()  # Convert the file to SQLite
        self.engine = DatabaseManager.get_engine(self.file)
        return self

    def set_rule(self, rule_id: int):
        self.rule = Rule.objects.get(id=rule_id)
        return self

    def set_table(self, table_name):
        self.table_name = table_name
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
        if self.table_name == "":
            raise ValueError(_("Table name is not set"))
        session = DatabaseManager.get_session(self.file)
        table = Table(self.table_name, MetaData(), autoload_with=self.engine)

        sql_builder = SQLBuilder(self.rule, table)
        sql, params = sql_builder.build()
        print(sql)

        query = text(sql).execution_options(render_postcompile=True)
        result = session.execute(query, params)
        rows = result.fetchall()
        columns = result.keys()

        df = pd.DataFrame(rows, columns=columns)
        execl_path = f"{self.file.get_full_path()}_{table.name}.xlsx"
        df.to_excel(execl_path, index=False, engine="openpyxl")
        url_path = execl_path.replace(str(settings.MEDIA_ROOT), "")
        if url_path[0] == "/":
            url_path = url_path[1:]

        return str(settings.MEDIA_URL) + url_path
