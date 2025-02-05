WORK_DIR=$(
    cd $(dirname $(dirname $0))
    pwd
)

cd $WORK_DIR

rm -f db.sqlite3
find $WORK_DIR -type d -name "migrations" | while read MIGRATIONS_DIR; do
    find $MIGRATIONS_DIR -type f ! -name "__init__.py" -delete
done

$WORK_DIR/scripts/initdb.sh
