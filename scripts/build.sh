WORK_DIR=$(
    cd $(dirname $(dirname $0))
    pwd
)

cd $WORK_DIR

image_name=data-filter-project
db_file=$WORK_DIR/db.sqlite3
need_initdb=false

docker container stop $image_name
docker container rm $image_name
docker build -t $image_name .

# if argument 1 is reset
if [ "$1" == "reset" ]; then
    rm -f $db_file
fi

if [ ! -f $db_file ]; then
    touch $db_file
    need_initdb=true
fi

docker run -d -p 8090:8000 -v $db_file:/app/db.sqlite3 --name $image_name $image_name

if [ "$need_initdb" = true ]; then
    docker exec -t $image_name bash -c "/app/scripts/initdb.sh"
    docker container restart $image_name
fi
