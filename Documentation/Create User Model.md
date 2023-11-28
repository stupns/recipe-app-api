[ <-- 3. Configure Database ](Configure%20Database.md)
# 4. Create User Model
___
## Step 1. Add user model tests:

Create file `test_models.py` in app>core>tests:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email,
                'sample123'
            )
            
            self.assertEqual(user.email, expected)

```
## Step 2. Implement User Model:

In app>core>models.py add next:
```python
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
```

You setup `AUTH_USER_MODEL` in settings.py:
```python
AUTH_USER_MODEL = 'core.User'
```
after make migrations: 
```commandline
docker-compose run --rm app sh -c "python manage.py makemigrations"

...
 ✔ Container recipe-app-api-db-1  Running                                                                                                                                                                                                                    
Migrations for 'core':
    core/migrations/0001_initial.py                                                                                                                                                                                                                     
        - Create model User
```
```commandline
docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
```
## Step 3. Require email input and add superuser support:

```python
def test_new_user_without_email_raises_error(self):
    """Test that creating a user without an email raises a ValueError."""
    with self.assertRaises(ValueError):
        get_user_model().objects.create_user('', 'test123')


def test_create_superuser(self):
    """Test creating a superuser."""
    user = get_user_model().objects.create_superuser(
        'test@example.com',
        'test123',
    )

    self.assertTrue(user.is_superuser)
    self.assertTrue(user.is_staff)
```

**Solution:**

In app>core>models.py add next:
```python

class UserManager(BaseUserManager):
    """Manager for users."""

def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
    ...
    
def create_superuser(self, email, password):
    """Create and return a new superuser."""
    user = self.create_user(email, password)
    user.is_staff = True
    user.is_superuser = True
    user.save(using=self._db)

    return user
```

____
> **Commits:**
>
> https://github.com/stupns/recipe-app-api/commit/632860f
> 
> https://github.com/stupns/recipe-app-api/commit/65efed4

 