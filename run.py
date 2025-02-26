import os
import webbrowser
import django
from django.core.management import execute_from_command_line
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_filter.settings")
django.setup()


def init():
    db_file = settings.DATABASES["default"]["NAME"]
    if os.path.exists(db_file):
        return
    if not os.path.exists(os.path.dirname(db_file)):
        os.makedirs(os.path.dirname(db_file))
    execute_from_command_line(["manage.py", "makemigrations"])
    execute_from_command_line(["manage.py", "migrate"])
    execute_from_command_line(
        [
            "manage.py",
            "shell",
            "-c",
            "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'email@example.com', '123456')",
        ]
    )


def run_server():
    webbrowser.open("http://127.0.0.1:8000")
    execute_from_command_line(["manage.py", "runserver", "--noreload"])


if __name__ == "__main__":
    init()
    run_server()
