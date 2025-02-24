# Data-filter Project

## Install Dependencies

Clone the repository and navigate to the `data-filter-project` directory.

```shell
git clone https://github.com/ipuppet/data-filter-project
cd data-filter-project
```

There are two ways to install the dependencies: using `pip` or using `docker`.

### Use Pip

> pip-tools is used to manage the dependencies.

```shell
pip install -r requirements.txt
```

#### Init Database

```shell
./scripts/initdb.sh
```

#### Reset Database

```shell
./scripts/resetdb.sh
```

#### Run Server

```shell
python manage.py runserver
```

### Use Docker

This will create a docker container named `data-filter-project`.

**Note:** The `build.sh` script will first remove any existing containers with the same name.

```shell
./scripts/build.sh
```

This will automatically initialize the database if it does not exist.

#### Reset Docker Database

```shell
./scripts/build.sh reset
```

## i18n

### Create `.po` file

`django-admin makemessages -l zh_Hans`

### Compile

`django-admin compilemessages`