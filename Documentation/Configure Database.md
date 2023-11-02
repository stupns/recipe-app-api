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
```yaml
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

## Step 3. 

