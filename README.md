# Data-filter Project

## Install Dependencies

Clone the repository and navigate to the `data-filter-project` directory.

```shell
git clone https://github.com/ipuppet/data-filter-project
cd data-filter-project
```

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

## i18n

### Create `.po` file

`django-admin makemessages -l zh_Hans`

### Compile

`django-admin compilemessages`

## pyinstaller

```shell
pyinstaller run.spec
```