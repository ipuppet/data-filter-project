WORK_DIR=$(
    cd "$(dirname "$(dirname "$0")")" || exit
    pwd
)
cd "$WORK_DIR" || exit

mkdir -p "$WORK_DIR"/data_filter/locale
django-admin makemessages -l zh_Hans
