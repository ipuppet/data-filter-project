from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DatabaseManager:
    _instances = {}

    @classmethod
    def get_db_url(cls, file):
        return f"sqlite:///{file.get_full_path()}.sqlite"

    @classmethod
    def get_engine(cls, file):
        if file.id not in cls._instances:
            cls._instances[file.id] = create_engine(cls.get_db_url(file))
        return cls._instances[file.id]

    @classmethod
    def get_session(cls, file):
        engine = cls.get_engine(file)
        Session = sessionmaker(bind=engine)
        return Session()

    @classmethod
    def close_engine(cls, file):
        if file.id in cls._instances:
            engine = cls._instances[file.id]
            engine.dispose()
            del cls._instances[file.id]
