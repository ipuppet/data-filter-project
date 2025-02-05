WORK_DIR=$(
    cd $(dirname $(dirname $0))
    pwd
)

cd $WORK_DIR

python manage.py makemigrations
python manage.py migrate
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'email@example.com', '123456')" | python manage.py shell
