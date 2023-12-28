[ <-- Implement filtering ](Implement%20filtering.md)
# 9. Deployment

## Step 1. Adding uWSGI to the Project

To prepare your Django application for production, integrating uWSGI as the application server is a crucial step.
uWSGI is a versatile and fast application server for serving Python applications, and it's commonly used
in production environments.

**Updating the Dockerfile**

Your Dockerfile needs to be updated to handle the uWSGI setup. This includes copying the `requirements.dev.txt` file,
setting up the environment, and defining the command **(CMD)** to run the application using uWSGI.

Here's the updated Dockerfile:
```yaml
# Dockerfile

# Other records
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts

ARG DEV=false
RUN python -m venv /py && \
    # Other records...
    build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \    <- linux-headers

    # Other records...
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

# Other records...
ENV PATH="/scripts:/py/bin:$PATH"

USER django-user

CMD ["run.sh"]
```

**Creating the run.sh Script**

Create a script named run.sh in the scripts directory. This script will be responsible for running necessary Django
management commands and starting the uWSGI server.

```shell
#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi
```
**Updating requirements.txt**

Add uWSGI to your requirements.txt file to ensure it's installed within the Docker environment.

```text
# requirements.txt

uwsgi>=2.0.19,<2.1
```
**Building the Docker Image**

After making these changes, rebuild your Docker image to ensure that uWSGI and other dependencies are correctly 
installed:
```commandline
docker-compose build
```

**Key Points**

- **uWSGI**: uWSGI serves as the application server for Django in production, handling requests and managing Python
processes.
- **Dockerfile**: The Dockerfile is configured to set up the necessary environment for running Django with uWSGI.
- **run.sh Script**: This script automates the process of running Django management commands and starting the uWSGI
server with appropriate configurations.

With these configurations, your Django application is now ready for deployment with uWSGI as the application server,
providing a robust and scalable production environment.

## Step 2. Creating Proxy Configurations

For efficient deployment, setting up a reverse proxy is essential. Nginx is commonly used for this purpose. It can
serve static files directly and forward other requests to your Django application running via uWSGI. The configuration
involves creating a template for the Nginx server block and a set of `uwsgi_params` to ensure smooth communication
between Nginx and the uWSGI server.

**Creating the Nginx Server Block Template**

You need to create an Nginx configuration template (**default.conf.tpl**) that will be filled in at runtime with
environment variables. This template defines how Nginx handles incoming requests.

Create proxy/default.conf.tpl:

```text
# proxy/default.conf.tpl
server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass              ${APP_HOST}:${APP_PORT};
        include                 /etc/nginx/uwsgi_params;
        client_max_body_size    10M;
    }
}
```
In this configuration:

- **listen ${LISTEN_PORT}**: Nginx listens on the port specified by the **LISTEN_PORT** environment variable.
- **location /static**: Serves static files from the **/vol/static** directory.
- **location /**: Forwards requests to the uWSGI server **(uwsgi_pass)** running your Django application.

**Adding uwsgi_params**

The `uwsgi_params` file contains parameters needed for Nginx to communicate with the uWSGI server.

Create `proxy/uwsgi_params`:

```text
# proxy/uwsgi_params

uwsgi_param QUERY_STRING $query_string;
uwsgi_param REQUEST_METHOD $request_method;
uwsgi_param CONTENT_TYPE $content_type;
uwsgi_param CONTENT_LENGTH $content_length;
uwsgi_param REQUEST_URI $request_uri;
uwsgi_param PATH_INFO $document_uri;
uwsgi_param DOCUMENT_ROOT $document_root;
uwsgi_param SERVER_PROTOCOL $server_protocol;
uwsgi_param REMOTE_ADDR $remote_addr;
uwsgi_param REMOTE_PORT $remote_port;
uwsgi_param SERVER_ADDR $server_addr;
uwsgi_param SERVER_PORT $server_port;
uwsgi_param SERVER_NAME $server_name;
```
These parameters ensure that Nginx passes the correct data to the uWSGI server.

**Updating run.sh**

The run.sh script should be modified to fill in the Nginx configuration template with environment variables and start
Nginx.

Update run.sh:

```shell
#!/bin/sh

set -e

# Fill in the Nginx config template with env vars and move to conf.d
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

# Start Nginx in the foreground
nginx -g 'daemon off;'
```

This script uses envsubst to substitute environment variables into the Nginx configuration template and then starts
Nginx.

**Key Points**

- **Nginx Configuration Template**: Allows dynamic configuration of Nginx based on environment variables, providing
flexibility for different deployment environments.
- **Serving Static Files**: Nginx efficiently handles serving static files, reducing the load on the Django/uWSGI
application server.
- **Proxy for uWSGI**: Forwarding requests to the uWSGI server allows Nginx to handle HTTP-related tasks, while uWSGI
focuses on running the Django application.
- **run.sh Script**: Automates the process of configuring Nginx and starting it in the foreground.

With these configurations, your deployment setup now includes a robust reverse proxy using Nginx, enhancing the
performance and scalability of your Django application in a production environment.

## Step 3. Creating Proxy Dockerfile

To set up the Nginx proxy in a Docker container, you'll create a dedicated Dockerfile in the `proxy` directory. 
This Dockerfile will be responsible for setting up the Nginx image, configuring the necessary environment variables,
and ensuring the correct permissions for the static files directory.

**Writing the Dockerfile for the Nginx Proxy**

Create `proxy/Dockerfile` with the following content:

```yaml
# proxy/Dockerfile

FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="stupnsdeveloper.com"

# Copy the configuration template, uwsgi parameters, and the run script
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

# Set environment variables
ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

# Switch to root to perform privileged operations
USER root

# Create a directory for static files and set permissions
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

# Define /vol/static as a volume
VOLUME /vol/static

# Switch back to the nginx user
USER nginx

# Command to run when starting the container
CMD ["/run.sh"]
```
In this Dockerfile:

- **Base Image**: You are using `nginxinc/nginx-unprivileged:1-alpine`, which is a lightweight and secure base image 
for Nginx.
- **Configuration Files**: Copies the `default.conf.tpl`, `uwsgi_params`, and `run.sh` script to the container.
- **Environment Variables**: Sets default values for **LISTEN_PORT**, **APP_HOST**, and **APP_PORT**. These can be 
overridden when running the container.
- **Permissions**: Creates a directory for static files and adjusts permissions to ensure Nginx can access them.
- **Switching Users**: Switches to the root user to perform operations that require elevated privileges, 
and then switches back to the Nginx user for security.

**Building the Docker Image**

Navigate to the `proxy` directory and build the Docker image:
```commandline
cd proxy
docker build .
```

**Key Points**

- **Nginx Configuration**: The Dockerfile sets up Nginx with the necessary configuration for serving static files and
proxying requests to the Django application.
- **Security**: By using an unprivileged Nginx base image and switching back to the Nginx user after performing
root-level operations, your setup enhances security.
- **Flexibility**: Environment variables provide flexibility, allowing you to easily configure the proxy settings
when running the container.

With this Dockerfile, you can now build a Docker image for your Nginx proxy, which will work in tandem with your
Django application container to efficiently serve your application in a production environment.

## Step 4. Creating Docker Compose Configuration for Deployment

You're setting up a `docker-compose-deploy.yml` file for deploying your application with Docker Compose. 
This configuration will orchestrate the deployment of your Django app, PostgreSQL database, and Nginx proxy.

**Writing the docker-compose-deploy.yml File**

Create docker-compose-deploy.yml with the following content:

```yaml
version: "3.9"

services:
  app:
    build:
      context: .
    restart: always
    volumes:
      - static_data:/vol/web
    environment:
      - DB_HOST=db
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASS=${DB_PASS}
      - SECRET_KEY=${DJANGO_SECRET_KEY}
      - ALLOWED_HOSTS=${DJANGO_ALLOWED_HOSTS}
    depends_on:
      - db

  db:
    image: postgres:13-alpine
    restart: always
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASS}

  proxy:
    build:
      context: ./proxy
    restart: always
    depends_on:
      - app
    ports:
      - 80:8000
    volumes:
      - static_data:/vol/static

volumes:
  postgres-data:
  static_data:
```
In this configuration:

- **App Service**: Builds and starts the Django application.
- **Database Service (db)**: Uses the `postgres:13-alpine` image for the database. Persistent data is stored in a volume.
- **Proxy Service**: Builds and starts the Nginx proxy, forwarding port 80 to 8000 inside the container.
- **Volumes**: Two volumes are defined - one for PostgreSQL data and one for static files.

**Creating a Sample .env File**

To ensure sensitive data is not hard-coded in your Docker Compose configuration, create an .env.sample file. 
This file serves as a template for setting environment variables.

Create `.env.sample`:

```text
DB_NAME=dbname
DB_USER=rootuser
DB_PASS=changeme
DJANGO_SECRET_KEY=changeme
DJANGO_ALLOWED=127.0.0.1
```

Users should create an .env file based on this sample and fill in their specific values.

**Key Points**

- **Service Configuration**: Each service in the Docker Compose file is configured with necessary settings, dependencies,
and environment variables.
- **Environment Variables**: The use of environment variables **(${VARIABLE_NAME})** allows for secure and flexible
configuration.
- **Volumes**: Persistent data for the database and static files for the Django app are managed using Docker volumes.
- **Proxy Setup**: The Nginx proxy forwards traffic to the Django application and serves static files.

With this Docker Compose configuration, you can deploy your entire application stack in a coordinated manner, 
ensuring each component is properly set up and interconnected. Remember to provide a .env file with actual values
for the environment variables during deployment.

## Step 5. Creating AWS account and user

[AWS login](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fus-east-2.console.aws.amazon.com%2Fec2%2Fhome%3FhashArgs%3D%2523Instances%253A%26isauthcode%3Dtrue%26region%3Dus-east-2%26state%3DhashArgsFromTB_us-east-2_3c02dc49f2f067d3&client_id=arn%3Aaws%3Asignin%3A%3A%3Aconsole%2Fec2-tb&forceMobileApp=0&code_challenge=gg9EoYdvhJ4q8rHOWGpLiDxjtIuh1gAVkAWC37QMMRY&code_challenge_method=SHA-256)

**Login**

MFA code -> Google authenticator

**Create user**

- Users -> add user -> *enter username, *enter password
- - In Attach existing policies directly -> * Enter AdministratorAccess
- - Create user *

## Step 6. Upload SSH Key to AWS

```commandline
cd ~/
cd .ssh
ls

aws_id_rsa	aws_id_rsa.pub	id_ed25519	id_ed25519.pub	known_hosts	known_hosts.old

ssh-keygen -t rsa -b 4096

Generating public/private rsa key pair.
Enter file in which to save the key (/.ssh/id_rsa): .ssh/aws_id_rsa
Enter password:

Complete!

cat aws_id_rsa.pub

ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQMpm4WHL8ih09jujKWDZWvdRWK+IucY19JdwfTbAfIN5g5qgm6xsIchFIyibApxd9OFToJr5JpW6Lvv
I+EC34bzZTyOCZYUUTAqoGw3101tWmfgRmgAsESIH0HLY7zMqbvQhVmybhTR7W7xf+X2JlFgU4rUYENdW50w== admin@admins-MBP.attlocal.net
```

Go to EC2:

- Key pairs -> Import key pair -> Paste key in field -> Import key pair

Created a new RSA SSH key named aws_id_rsa for use when connecting to AWS. The key was stored in the ~/.ssh/ directory.
Generated an SSH key using the ssh-keygen command.
Created and saved the key, confirming the action by pressing Enter.
Displayed the content of the public key (cat aws_id_rsa.pub).

## Step 7. Create EC2 instance

**Launch an instance**

1. `Name`: **recipe-api-dev-server**
2. `AMI`: **Amazon Linux 2 AMI (HVM) - Kernel 5.10, SSD Volume Type**
2.1 `Architecture`: **64-bit(x86)**
3. `Instance type`: **t2.micro**
4. `Key pair`: **admin-local-machine**
5. `Allow SSH trafic from` : **anywhere**
5.2 **Allow HTTP trafic from the internet**
6. `Configure storage`: **30**
7. **Launch instance**

Next open instance, and copy IPv4 address:

**Public IPv4 address**: `18.222.194.81`

Login in terminal:

```commandline
ssh-add aws_id_rsa
ssh ec2-user@18.222.194.81
-> yes

[ec2-user@ip-172-31-34-242 ~]$
```

## Step 8. Setup GitHub deploy key

In the terminal cc2:

```commandline
ssh ec2-user@18.222.194.81

[ec2-user@ip-172-31-34-242 ~]$ ssh-keygen -t ed25519 -b 4096

Complete!

cat ~/.ssh/id_ed25519.pub

*Copy key
```

In GitHub repositories -> recipe-app-api:
- Settings: Deploy keys -> Add deploy key
- - Title: server
- - Key: paste the copied key

Generated a new Ed25519 SSH key on EC2 for use with GitHub.
Generated the key using ssh-keygen and displayed the content of the public key with cat ~/.ssh/id_ed25519.pub.
Created a new deploy key on the GitHub repository settings page using the copied key.

## Step 9. Install Docker, Compose and Git

Use the below commands to configure the EC2 virtual machine running Amazon Linux 2.

Install Git:

```sh
[ec2-user@ip-172-31-34-242 ~]$ sudo yum install git -y
```
Install Docker, make it auto start and give `ec2-user` permissions to use it:

```sh
[ec2-user@ip-172-31-34-242 ~]$ sudo amazon-linux-extras install docker -y
[ec2-user@ip-172-31-34-242 ~]$ sudo systemctl enable docker.service
[ec2-user@ip-172-31-34-242 ~]$ sudo systemctl start docker.service
[ec2-user@ip-172-31-34-242 ~]$ sudo usermod -aG docker ec2-user
```
Note: After running the above, you need to logout by typing `exit` and re-connect to the server in order for the 
permissions to come into effect.

Install Docker Compose:
```sh
[ec2-user@ip-172-31-34-242 ~]$ sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
[ec2-user@ip-172-31-34-242 ~]$ sudo chmod +x /usr/local/bin/docker-compose
```

**Explanation:**

- **Git Installation**: Installs Git, a version control system, using the package manager yum.
- **Docker Installation**: Installs Docker using `amazon-linux-extras`, enables automatic startup of the Docker service,
starts the Docker service, and grants the `ec2-user` permission to use Docker.
- **Docker Compose Installation**: Downloads Docker Compose binary from GitHub, makes it executable, and places it in
the `/usr/local/bin/` directory.



## Step 10. Clone and configure project

Clone the Project Repository:

```shell
[ec2-user@ip-172-31-34-242 ~]$ git clone git@github.com:stupns/recipe-app-api.git
cd recipe-app-api
git pull origin
cp .env.sample .env
nano .env
```
In the editor, update the .env file with the following content:

```text
DB_NAME=recipedb
DB_USER=recipeuser
DB_PASS=changeme123
DJANGO_SECRET_KEY=jkh123hj21g412k3jh213kjh412
DJANGO_ALLOWED_HOSTS=ec2-18-222-194-81.us-east-2.compute.amazonaws.com
```
Save the changes.

## Step 11. Run service

Run the following command to start the services using the specified Docker Compose configuration:

```shell
docker-compose -f docker-compose-deploy.yml up -d
```
After running the services, you can access the Django admin interface at:

http://ec2-18-222-194-81.us-east-2.compute.amazonaws.com/admin

**Create a Superuser**

To create a superuser for the Django admin, use the following command:
```shell
docker-compose -f docker-compose-deploy.yml run --rm app sh -c "python manage.py createsuperuser"
```
![1.png](Img%2F1.png)

### Viewing Logs

To view container logs, run:

```sh
docker-compose -f docker-compose-deploy.yml logs
```

These commands will help you manage the deployment, create a superuser, and view logs for debugging.

## Step 12. Updating service

create core/tests/test_health_check.py:

```python
# core/tests/test_health_check.py:

from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


class HealthCheckTests(TestCase):
    """Test the health check API."""

    def test_health_check(self):
        """Test health check API."""
        client = APIClient()
        url = reverse('health-check')
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

```

in core/views.py:

```python
# core/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    """Returns successful response."""
    return Response({'healthy': True})
```

in app/urls.py:

```python
# app/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health-check/', core_views.health_check, name='health-check'),
    # other patches...
```

```commandline
git add *
git commit -am "add files"
git push origin
```

Open terminal EC2:

```shell
cd recipe-app-api
git pull origin

docker-compose -f docker-compose-deploy.yml build app
```

To apply the update, run:

```sh
docker-compose -f docker-compose-deploy.yml up --no-deps -d app
```

The `--no-deps -d` ensures that the dependant services (such as `proxy`) do not restart.

![2.png](Img%2F2.png)

____
> **Commits:**
>* https://github.com/stupns/recipe-app-api/commit/1d34631 (origin/main, origin/br-13-deployment-finish, origin/HEAD,
main) Adding last files for deployment projects.
>* https://github.com/stupns/recipe-app-api/commit/8a355eb fix syntaxes
>* https://github.com/stupns/recipe-app-api/commit/24c9d36 fix syntaxes
>* https://github.com/stupns/recipe-app-api/commit/8b487d0 (origin/br-12-deployment) Adding test deploying files and 
checking status.
