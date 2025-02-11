WORK_DIR=$(
    cd $(dirname $(dirname $0))
    pwd
)

cd $WORK_DIR

mkdir -p $WORK_DIR/data_filter/locale
django-admin makemessages -l zh_Hans
