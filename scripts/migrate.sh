WORK_DIR=$(
    cd "$(dirname "$(dirname "$0")")" || exit
    pwd
)
cd "$WORK_DIR" || exit

python manage.py makemigrations
python manage.py migrate
