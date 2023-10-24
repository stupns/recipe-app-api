[ <-- 1. Initialization ](Initialization.md)
# 2. Configure GitHub Actions
___
## Configure DockerHub Credentials
https://hub.docker.com/settings/security

Step 1. Create new token Account Settings > Security > Access Tokens:
 - New Access Token: "recipe-app-api-github-actions" - Generate
 - copy token *

Step 2. Open github repository > Settings > Secrets:
 * New Repository secrets: 
   - name: DOCKERHUB_USER
   - value: stupns

   - name: DOCKERHUB_TOKEN (*you can update previous secret.)
   - value: paste token*


Step 3. Create folder .github > workflows > checks.yml:

checks.yml:
```yaml
---
name: Checks

on: [push]

jobs:
  test-lint:
    name: Test and Lint
    runs-on: ubuntu-20.04
    steps:
      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKERHUB_USER }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Checkout
        uses: actions/checkout@v2
      - name: Test
        run: docker-compose run --rm app sh -c "python manage.py test"
      - name: Lint
        run: docker-compose run --rm app sh -c "flake8"
```