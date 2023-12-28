# recipe-app-api
Recipe API project on DJANGO

http://ec2-18-222-194-81.us-east-2.compute.amazonaws.com/api/docs/

___
## Description

This a Django web application that provides an API for managing recipes. The key steps and stages of development include:

- **User Model Creation**: You created a user model that allows user registration and authentication.

- **Adding User Avatar**: Extended user capabilities by allowing the upload and storage of avatars.

- **Recipe Management**: Implemented functionality for adding, viewing, and editing recipes.

- **Fixes and API Enhancement**: Addressed issues, added functionality, and expanded API capabilities for recipes.

- **Adding Images to Recipes**: Implemented the ability to upload and store images for each recipe.

- **Configuration and Extension of Django Admin Interface**: Configured the Django admin interface for more convenient user and recipe management.

- **Fixes and API Enhancement**: Addressed issues, added functionality, and expanded API capabilities for recipes.

- **Recipe Filtering by Tags and Ingredients**: Added the ability to filter recipes by tags and ingredients for convenient searching.

- **Django Admin Interface Customization**: Customized the Django admin interface to improve the management and usability of user models.

- **API Documentation**: Configured API documentation using drf-spectacular for better understanding and interaction with the API.

- **Deployment on AWS EC2**: Deployed the project on an AWS EC2 server using Docker and configured necessary settings.

- **GitHub Deploy Key Setup**: Set up a deploy key on GitHub for secure access to the repository from the EC2 instance.

- **AWS Account and User Setup**: Created an AWS account, set up a user with appropriate permissions, and configured multi-factor authentication (MFA).

- **SSH Key Upload to AWS**: Generated and uploaded an SSH key to AWS for secure access to EC2 instances.

- **Docker, Compose, and Git Installation**: Installed Docker, Docker Compose, and Git on the EC2 instance for project deployment.

- **Clone and Configure Project**: Cloned the project from GitHub, configured environment variables, and set up the project for execution.

- **Service Execution**: Ran the Docker Compose command to start the services, allowing access to the application.

- **Documentation Update**: Documented steps for setting up Docker, Compose, Git, cloning the project, and running the service.

- **Django Admin Customization**: Customized the Django admin interface for better management of users.

- **URL Configuration**: Updated URL configuration to include API schema and documentation endpoints.

This comprehensive development process results in a fully functional recipe management application with an API, user
authentication, and enhanced administrative capabilities.
___

## Stages of development

___
- [1.Initialization.md](Documentation%2F1.Initialization.md)
- [2.Github Actions.md](Documentation%2F2.Github%20Actions.md)
- [3.Configure Database.md](Documentation%2F3.Configure%20Database.md)
- [4.Create User Model.md](Documentation%2F4.Create%20User%20Model.md)
- [5.Setup Django Admin.md](Documentation%2F5.Setup%20Django%20Admin.md)
- [6.Api Documentation.md](Documentation%2F6.Api%20Documentation.md)
- [7.Build User Api.md](Documentation%2F7.Build%20User%20Api.md)
- [8.Build Recipe Api.md](Documentation%2F8.Build%20Recipe%20Api.md)
- [9.Build Tags API.md](Documentation%2F9.Build%20Tags%20API.md)
- [10.Build Ingredients API.md](Documentation%2F10.Build%20Ingredients%20API.md)
- [11.Recipe Image API.md](Documentation%2F11.Recipe%20Image%20API.md)
- [12.Implement filtering.md](Documentation%2F12.Implement%20filtering.md)
- [13.Deployment.md](Documentation%2F13.Deployment.md)

___

## Setup

For run on local machine:

1. Git clone.
2. docker build .
3. docker-compose build
4. docker-compose up
5. docker-compose run --rm app sh -c "flake8"

For AWS EC2:

```shell
ssh ec2-user@18.222.194.81
cd recipe-app-api
git pull origin

docker-compose -f docker-compose-deploy.yml build app
```

To view container logs, run:

```sh
docker-compose -f docker-compose-deploy.yml logs
```

To apply the update, run:

```sh
docker-compose -f docker-compose-deploy.yml up --no-deps -d app
```

The `--no-deps -d` ensures that the dependant services (such as `proxy`) do not restart.

For more detailed information see:
[13.Deployment.md](Documentation%2F13.Deployment.md)
___

Screenshot:

![3.png](Documentation%2FImg%2F3.png)
![4.png](Documentation%2FImg%2F4.png)
![5.png](Documentation%2FImg%2F5.png)
![6.png](Documentation%2FImg%2F6.png)
![7.png](Documentation%2FImg%2F7.png)
![8.png](Documentation%2FImg%2F8.png)
![9.png](Documentation%2FImg%2F9.png)
![10.png](Documentation%2FImg%2F10.png)