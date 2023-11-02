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