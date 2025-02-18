WORK_DIR=$(
    cd "$(dirname "$(dirname "$0")")" || exit
    pwd
)
cd "$WORK_DIR" || exit

rm -f db.sqlite3
find "$WORK_DIR" -type d -name "migrations" | while read -r MIGRATIONS_DIR; do
    find "$MIGRATIONS_DIR" -type f ! -name "__init__.py" -delete
done

"$WORK_DIR"/scripts/initdb.sh
