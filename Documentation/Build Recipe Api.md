[ <-- . Build User Api  ](Build%20User%20Api.md)
# 5. Build Recipe Api
You're on the right track for developing a Recipe API in your Django application. Here's how you can proceed with the
outlined steps:
___
## Step 1. Write Test for Recipe Model

In the core/tests/test_models.py, you'll write a test to verify the creation of a recipe. This test ensures that your
model is set up correctly and can create recipe instances.

Update the test_models.py as follows:

```python
# core/tests/test_models.py

from decimal import Decimal

from .. import models
...

class ModelTests(TestCase):
    """Test models."""
    ...
    
    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample recipe description.',
        )
```

## Step 2. Implement recipe model

In app/core/models.py, define the Recipe model. This model will be used to store recipe details in your database.

Update models.py as follows:

```python
# app/core/models.py

class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

```

**Register Recipe Model in Admin and Run Migrations**

Next, you need to register the Recipe model in the admin.py to manage it via the Django admin site:

```python
# app/core/admin.py

from django.contrib import admin
from core import models

...
admin.site.register(models.Recipe)
```
Finally, run the following Docker command to create migrations for your new model:
```commandline
docker-compose run --rm app sh -c "python manage.py makemigrations"
```

## Step 3. Create recipe app

Run the Docker command to create a new Django app named recipe:

```commandline
docker-compose run --rm app sh -c "python manage.py startapp recipe"
```
**Clean Up Unnecessary Files**

After creating the app, you'll need to remove some files that are not immediately necessary.
Execute these commands in your project directory:

- `recipe/migrations.py`
- `recipe/admin.py`
- `recipe/models.py`
- `recipe/tests.py`

Create a **tests** directory with an **___init__.py_** file inside the recipe app. This is where you'll later add your
test files.

Finally, add the recipe app to your Django project settings. This step is crucial for Django to recognize the app.

Open your **`settings.py`** file and update the INSTALLED_APPS section:
```python
# settings.py

INSTALLED_APPS = [
    ...,
    'recipe',
]
```

## Step 4. Write tests for listing recipes

Here is your provided test script for **`test_recipe_api.py`**, formatted and explained:

```python
#test_recipe_api.py

"""
Tests for recipe API.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe,
)

from recipe.serializers import (
    RecipeSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title.',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user@example.com', 'test123')
        # self.user = create_user(email='user@example.com', password='test123') - simple finished example
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        # other_user = create_user( - simple finished example
        #    email='other@example.com',
        #    password='password123'
        #)
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
```
**Key Points:**
- create_recipe: A helper function to create sample recipes.
- **`PublicRecipeAPITests`**: Tests to ensure that unauthenticated requests are not allowed.
- **`PrivateRecipeApiTests`**: Tests for authenticated requests, including checking that only recipes for the
authenticated user are returned.

- This setup will help validate the core functionality of your recipe listing API, ensuring that it
behaves as expected under different scenarios.

## Step 5. Implement Recipe listing API

In your recipe app, create a **`serializers.py`** file for the recipe model:

```python
# serializers.py

"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import (
    Recipe,
)

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link'
        ]
        read_only_fields = ['id']
```

Next, define the view for your recipe API. Make sure to use the correct serializer for the `RecipeViewSet`. It seems like
you mentioned `RecipeDetailSerializer`, which might be a detailed version of the recipe serializer. Ensure that you have
this serializer defined in your serializers.py or use `RecipeSerializer` if that's not the case.

```python
# recipe/views.py
"""
Views for the recipe APIs.
"""

from rest_framework import (
    viewsets,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,

)
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id') # need optimize to new format

```

**Update `recipe\urls.py`**
Define URL patterns for your recipe API using Django's DefaultRouter:

```python
# recipe/urls.py

"""
URL mappings for the recipe API.
"""
from django.urls import (
    path,
    include,
)

from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
```

Lastly, update your project's main URL configuration to include the recipe app URLs:

```python
# app/urls.py
urlpatterns = [
    ...,
    path('api/recipe/', include('recipe.urls')),
]
```
With these steps, your Recipe Listing API will be set up. It will allow authenticated users to list, create, update,
and delete recipes. Ensure that all components (models, serializers, views, and URLs) are correctly defined and
integrated for the API to function smoothly.

## Step 6. Write tests for recipe details API

To test the recipe details API in your Django project, you'll need to update `test_recipe_api.py`. This test will ensure
that the API correctly retrieves the details of a specific recipe. Before you begin, make sure that you have defined the
**RecipeDetailSerializer** in your serializers.py.

Here's the updated code for your test file:

```python
# test_recipe_api.py

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

# Other code...

class PrivateRecipeApiTests(TestCase):
    # Other test methods...
    
    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
```
**Key Points:**

- **`detail_url(recipe_id)`**: A helper function to create a URL for the recipe detail view. Make sure the URL name
(recipe:recipe-detail) matches the one defined in your URL configurations.
- **`test_get_recipe_detail`**: This test ensures that the recipe detail view returns the correct data for a given
recipe. It uses RecipeDetailSerializer to serialize the data for comparison. 

With these tests, you can validate the functionality of your recipe detail API, ensuring it correctly
retrieves detailed information for individual recipes. Remember to run your tests after implementing the corresponding
API view to verify that everything is working as expected.

## Step 7. Implement recipe detail API

To implement the recipe detail API, you'll extend the functionality in `recipe/serializers.py` and recipe/views.py.
Here's how you can do it:

**Update `recipe/serializers.py`**
First, extend the **RecipeSerializer** to create a **RecipeDetailSerializer** for detailed recipe information. 
This serializer will include additional fields, such as description, which may not be needed in the list view.

```python
#recipe/serializers.py

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
```

**Update recipe/views.py**
Next, update the **RecipeViewSet** in views.py to use the correct serializer based on the action. In your case, you want
to use the RecipeDetailSerializer for the retrieve action (which corresponds to getting recipe details)
and **RecipeSerializer** for the list action.

```python
# recipe/views.py

...
class RecipeViewSet(viewsets.ModelViewSet):
    # other code...

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer


        return self.serializer_class
```
**Considerations:**
- Ensure that the get_serializer_class method in **RecipeViewSet** correctly returns **RecipeDetailSerializer** for 
the retrieve action and **RecipeSerializer** for other actions like list.
- You have used `self.serializer_class` in your code snippet, but it's not necessary in this context since the method 
 `get_serializer_class` handles the selection of the appropriate serializer.
- These updates will allow your API to return detailed recipe information when retrieving a single recipe and a more
 concise representation when listing multiple recipes.

With these changes, your recipe detail API should be fully functional, providing detailed information for individual
recipes while maintaining efficient, less detailed responses for recipe lists.

## Step 8. Write tests for creating recipes.

To test the functionality of creating recipes through your API, you'll add a new test method to the 
**PrivateRecipeApiTests** class in `test_recipe_api`.py. This test will ensure that authenticated users can successfully
create new recipes and that the created recipes have the correct data and are associated with the correct user.

Here's how you can implement this test:
```python
# test_recipe_api.py

# Other imports and test cases...

class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""
    
    # Other setup methods and test cases...
    
    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)  # /api/recipes/recipe

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

# Additional test methods...
```
**Key Points:**
- `**test_create_recipe**:` This test method sends a POST request to the recipe creation endpoint with a payload 
containing recipe data. It then checks if the recipe is created successfully (status.HTTP_201_CREATED), verifies 
that the data in the created recipe matches the sent payload, and confirms that the recipe is associated with the 
correct user.
- `**RECIPES_URL**:` Ensure that this variable correctly points to your recipe creation endpoint.

With this test, you will be able to verify that your recipe creation API endpoint functions correctly,
allowing authenticated users to create new recipes. Remember to run your tests regularly to ensure the API is working 
as expected throughout the development process.

## Step 9. Implement create Recipe API

To enable the creation of recipes through your API, you will need to update the **RecipeViewSet** in views.py of your 
recipe app. Specifically, you'll override the perform_create method to ensure that the recipe is associated with the
user who
creates it.

Here's how you can implement this in your views.py:

```python
# recipe/views.py

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    # other code

    def perform_create(self, serializer):
        """Create new recipe."""
        serializer.save(user=self.request.user)
```

**Key Points:**
- **`perform_create`**: This method is overridden to associate the newly created recipe with the user who is making
the request.The `**serializer.save(user=self.request.user)**` call ensures that the `**user**` field of the recipe is
set to the current user.
- The rest of the **`RecipeViewSet`** class remains as previously defined, handling different actions like list, 
retrieve, and now create.

With this implementation, authenticated users will be able to create new recipes via your API. The recipes they create
will be linked to their user account, allowing for personalized recipe management.

## Step 10. Add additional tests

Your additional tests for the Recipe API in `test_recipe_api.py` are essential for ensuring robustness and security. 
These tests cover partial and full updates of recipes, deletion, and unauthorized access to recipes owned by other
users. Let's break down these test cases:

**Test for Partial Update of a Recipe**

This test ensures that a PATCH request to a recipe URL updates the specified fields while leaving others unchanged.

```python
# test_recipe_api.py

# Other imports and test cases...

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)



class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123') # update here
        self.client.force_authenticate(self.user)

    # other ...

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(       # update here
            email='other@example.com',
            password='password123'
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

    # other ...
```

```python
    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title.',
            link=original_link,
        )

        payload = {'title': 'New recipe title.'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
```

**Test for Full Update of a Recipe**

This test checks if a **PUT** request to a recipe URL updates all the fields of a recipe.
```python
    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title.',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description.',
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
```
**Test to Prevent Unauthorized User Update**

This test ensures that a recipe's user field cannot be changed via the API.
```python
    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
```
**Test for Deleting a Recipe**

This test confirms that a **DELETE** request to a recipe URL deletes the recipe.
```python
    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

```
**Test to Prevent Deleting Others' Recipes**

This test ensures that a user cannot delete a recipe created by another user.
```python
    def test_recipe_others_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())
```

**Additional Notes**
- Make sure to import all necessary modules and classes at the beginning of the file.
- Remember to define the `**create_user**` and `**create_recipe**` helper functions if they are not already defined.
- Verify that your URL names in `detail_url` match those defined in your Django URL configurations.

With these tests, you will comprehensively cover various scenarios for managing recipes, ensuring your API behaves
correctly in terms of data integrity and access control.

____
> **Commits:**
>* https://github.com/stupns/recipe-app-api/commit/7383b20 (origin/br-7-build-recipe-api) Build a recipe api.
>
>* https://github.com/stupns/recipe-app-api/commit/f119dc0 Build a recipe api.
>
>* https://github.com/stupns/recipe-app-api/commit/95f5fed Build a recipe api.

