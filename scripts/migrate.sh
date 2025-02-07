WORK_DIR=$(
    cd $(dirname $(dirname $0))
    pwd
)

cd $WORK_DIR

python manage.py makemigrations
python manage.py migrate
