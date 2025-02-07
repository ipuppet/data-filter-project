import pandas as pd
from .models import File


class FileProcessor:
    def __init__(self, file: File):
        self.file = file

    def process(self):
        print(f"Processing file: {self.file.get_full_path()}")
        df = pd.read_excel(self.file.get_full_path())
        print(df)
        print(df.columns)
