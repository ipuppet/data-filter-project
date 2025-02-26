WORK_DIR=$(
    cd "$(dirname "$(dirname "$0")")" || exit
    pwd
)
cd "$WORK_DIR" || exit

"$WORK_DIR"/scripts/migrate.sh
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'email@example.com', '123456')" | python manage.py shell
