[ <-- 2. Configure GitHub Actions ](Github%20Actions.md)
# 3. Configure Database
___
## Step 1. Add database service:

In docker-compose.yml set a name for database container:

```yaml
    ...
    environment:
      - DB_HOST=db
      - DB_NAME=devdb
      - DB_USER=devuser
      - DB_PASS=devpass
      - DEBUG=1
    depends_on:
      - db

  db:
    image: postgres:13-alpine
    volumes:
      - dev-db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=devdb
      - POSTGRES_USER=devuser
      - POSTGRES_PASSWORD=devpass

volumes:
  dev-db-data:
```  


The volume **dev-db-data** is defined in the volumes section. This means that the database data will be stored on the
host’s disk and won't be lost when the database container is stopped or removed.

Up container:
```commandline
docker-compose up

... successfull!
```
## Step 2. Install Database adaptors

Setups independies for work with Postgres in Dockerfile:
```dockerfile
...
ARG DEV=false
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    ...
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    ...
```

Add in requirements library for work with Postgres to container:

```
...
psycopg2>=2.8.6,<2.9

```
Re-build containers:
```command
docker-compose down
docker-compose build

... Successfull!
```

## Step 3. Configure database in Django

Go tells Django to connect to a PostgreSQL database using the credentials and host provided through the environment
variables.
settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}
```

!! **_Don`t forget remove ~~db.sqlite3~~ from directory_**.

## Step 4. Create core app 

Run command create app in Django:
```commandline
recipe-app-api % docker-compose run --rm app sh -c "python manage.py startapp core"

Creating recipe-app-api_db_1 ... done
Creating recipe-app-api_app_run ... done
```
Add app in settings Django:

settings.py:
```python
INSTALLED_APPS = [
    ...
    'django.contrib.staticfiles',
    'core',
]
```

## Step 5. Write tests for wait_for_db command

Create folder with file core>management>wait_for_db.py.
Django command to wait for the database to be available.
wait_for_db.py:
```python
import time
from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """Entrypoint command to wait for db."""
        self.stdout.write('Waiting for database ...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
```

So, when u enter next command, u see :
```commandline
docker-compose run --rm app sh -c "python manage.py wait_for_db"

...
 ✔ Container recipe-app-api-db-1  Started                                                                                                                                                                                                                      0.9s 
[+] Building 0.0s (0/0)                                                                                                                                                                                                                        docker:desktop-linux
Waiting for database ...
Database available!
```

## Step 6. Update Docker Compose and CI/CD

In checks.yml need update line for `wait_for_db`:
```yaml
---
...
        run: docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py test"
...
```

Update the line in docker-compose.yml related to database migration and checking for availability:

```yaml
    ...
    command: >
      sh -c "python manage.py wait_for_db && 
             python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
```  

____
> **Commits:**
> 
> https://github.com/stupns/recipe-app-api/commit/34354236c875cff851fa20c1fd3a95ba04fc234a
> https://github.com/stupns/recipe-app-api/commit/34354236c875cff851fa20c1fd3a95ba04fc234a
 