[ <-- . Build Recipe Api  ](Build%20Recipe%20Api.md)
# 5. Build Tags API
It appears you're progressing to build a Tags API, which likely involves associating tags with recipes. However,
the provided test code focuses on the creation of a recipe rather than anything specific to tags. If you're planning
to introduce tags, you'll need tests that also handle the creation and association of tags with recipes.

___
## Step 1. Write test for recipe model

In core/tests/test_models.py, you should add a test to ensure that the creation of a tag works as expected. This test 
will validate the basic functionality of the Tag model.

In `core\tests\test_models`:

```python
# core\tests\test_models.py

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """Test models."""

    # Other tests...

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)
```

**Implementing Tag and Recipe Models**

In `core/models.py`
Modify your **`Recipe`** and **`Tag`** models to establish their relationship. A many-to-many relationship
(`**ManyToManyField**`) is appropriate if a recipe can have multiple tags and a tag can be associated with multiple
recipes.

```python
#core\models.py

class Recipe(models.Model):
    """Recipe object."""
    # Others fields ...
    tags = models.ManyToManyField('Tag')


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
```
**Database Migrations**

Run the following command to create migrations for your new models:
```commandline
docker-compose run --rm app sh -c "python manage.py makemigrations"
```

**Registering Tag in Admin**

In `core/admin.py`, register the **Tag** model to manage it via the Django admin interface.

```python
# core\admin.py

# Other model registrations...
admin.site.register(models.Tag)
```

**Next Steps**

- After implementing these changes, you should run your tests to ensure the Tag model works as expected.
- You may also want to create tests for associating tags with recipes and filtering recipes by tags, which are likely
key features of your Tags API.
- Ensure that your API views and serializers are updated to handle tags appropriately, including creating, listing,
updating, and deleting tags.

By following these steps, you will lay a solid foundation for your Tags API, ensuring that it integrates well with
your existing Recipe model and meets the functional requirements of your application.

## Step 2. Write tests for listing tags

You've outlined a detailed approach for testing the functionality of listing tags in your Tags API. Your tests will
ensure that only authenticated users can retrieve a list of tags and that users can only access their own tags. Here's
an overview of your test cases in test_tags_api.py:

**PublicTagsApiTests**

These tests are designed to validate that authentication is required for accessing the tags API.
```python
# recipe\tests\test_tags_api.py

"""
Tests for the tags API.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Tag,
    Recipe,
)
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
```

**PrivateTagsApiTests**

These tests check the functionality for authenticated requests, ensuring that tags are correctly retrieved and are
limited to those created by the authenticated user.
```python

class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
```

**Key Points**

- Ensure you have the `**TagSerializer**` implemented in your recipe/serializers.py file.
- The **`TAGS_URL`** should correctly point to your tags listing endpoint. Ensure it matches the URL name defined
in your URL configurations.
- The test `**test_tags_limited_to_user**` is crucial for verifying that users can only access their own tags,
enhancing the security and integrity of your API.

With these tests in place, you'll be able to validate that your Tags API behaves as expected in both authenticated and
unauthenticated contexts, ensuring that it handles tag listings correctly. Make sure to run these tests after
implementing the corresponding API views and serializers to confirm that everything is working as intended.

## Step 3. Implement tag listening API

ou're on the right track with implementing your Tag Listing API.
Here's a breakdown of the changes you'll make in your Django project.

**Create `TagSerializer` in `recipe/serializers.py`**

You'll start by defining a **TagSerializer** to handle the serialization of tag data.
This serializer will convert tag instances to and from JSON format.

```python
#recipe\serializers.py

# Others classes...
from core.models import (
    Recipe,
    Tag,
)

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
```

**Define `TagViewSet` in `recipe/views.py`**

Next, create a **TagViewSet** to handle requests related to tags.
Since you're initially implementing tag listing functionality, you'll use **ListModelMixin** and **GenericViewSet**.

```python
# recipe\views.py

from rest_framework import (
    viewsets,
    mixins,
    status,
)

from core.models import (
    Recipe,
    Tag,
)

# Other classes ...

class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet): # need later optimize
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]  # need later optimize
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve queryset to authenticated user."""
        return  self.queryset.filter(user=self.request.user).order_by('-name')
```

**Update URL Configuration in `recipe/urls.py`**

Finally, add the **TagViewSet** to your URL router to create the endpoint for tags.

```python
# recipe\urls.py

# Other routes...
router.register('tags', views.TagViewSet)
```

**Notes and Considerations**

- The **TagViewSet** uses the **ListModelMixin** to provide listing functionality. As you expand your API,
you might add more mixins or change to **ModelViewSet** if you need full **CRUD** (Create, Read, Update, Delete)
capabilities.
- The **get_queryset** method ensures that users will only see their own tags, aligning with the principle of
data ownership and privacy.
- Make sure your URL names and paths in `recipe/urls.py` are set up correctly to match your API's structure.

By following these steps, you'll establish the foundational aspects of your Tags API, allowing authenticated users
to view a list of their tags. This setup also sets the stage for further expansion of tag-related
functionalities in your API.

## Step 4. Write tests for updating tags.

Writing tests for updating tags is an important step in ensuring that your Tags API functions correctly. Let's go
through the test you've outlined for updating a tag:

**Test for Updating a Tag**

This test checks whether a tag can be successfully updated using a PATCH request.
It creates a tag, updates it with a new name, and then checks if the update was successful.

```python
#tests\test_tags_api.py

# Other imports and test cases...
# Others methods...

def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])

class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""
    
    # Other test methods...
    
    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

```

**Key Points**

- The `**detail_url**` function generates the URL for a specific tag's detail view. Ensure the URL name 
`**recipe:tag-detail**` matches the one defined in your URL configurations.
- In **PrivateTagsApiTests**, the setUp method prepares an authenticated client and a test user for the tests.
- **`test_update_tag`** checks the functionality of updating a tag's name. It creates a tag, sends a PATCH request
to update it, and then verifies if the update was applied correctly.

With this test, you'll be able to verify that your Tags API allows authenticated users to update their tags.
After implementing the corresponding view for handling PATCH requests in your Tags API, run these tests to
ensure everything is working as expected.

## Step 5. Implement Update Tag API

To enable the functionality of updating tags in your Tags API, you will modify the **`TagViewSet`** in 
`recipe/views.py`. By including **mixins.UpdateModelMixin**, you're allowing your API to handle PATCH and PUT requests
for updating tag instances.

Here's how you can update the `**TagViewSet**`:

```python
#recipe\views.py
                 
class TagViewSet(mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet): # need later optimize
    """Manage tags in the database."""
    ...

```

**Key Points**

- By adding `**mixins.UpdateModelMixin**`, the **TagViewSet** now supports handling update requests. This mixin
provides the `**.update()**` and `**.partial_update()**` actions.
- The **`get_queryset`** method ensures that users only have access to their own tags, which is important for
maintaining user data isolation and security.
- Remember to keep your authentication and permission classes in place to ensure that only authenticated
users can access and modify tags.

With this implementation, your Tags API will now support updating tags, allowing users to
modify existing tags' details. After making these changes, be sure to test your API to ensure that the
update functionality is working correctly and securely.


## Step 6. Write tests for deleting tags

Test for deleting tags is a crucial part of ensuring the robustness of your Tags API. It verifies
that authenticated users can delete their tags and that the tags are indeed removed from the database.
Here's a breakdown of your test case:

**Test for Deleting a Tag**

This test ensures that an authenticated user can delete a tag and that the tag is no longer present
in the database after deletion.

```python
# recipe\tests\test_tags_api.py

# Other imports and test cases...

class PrivateTagsApiTests(TestCase):
    """Test authenticated API requests."""
    
    # Others test methods...
    
    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
```

**Key Points**

- The `**detail_url**` function generates the URL for a specific tag's detail view. 
Ensure that the URL name `**recipe:tag-detail**` matches the one defined in your URL configurations.
- The **`test test_delete_tag`** creates a tag, deletes it, and then checks that the tag no longer exists in the
database. The status code HTTP_204_NO_CONTENT indicates successful deletion.
- This test ensures that the delete functionality of your Tags API is working as expected and that tags
are properly removed upon request.

After implementing the corresponding delete functionality in your API view, run this test to confirm that
tags can be deleted correctly by authenticated users. This will help maintain the integrity and 
cleanliness of the user's data in your application.

## Step 7. Implement delete tag API

To enable the deletion of tags in your Tags API, you'll need to update the **`TagViewSet`** in `recipe/views.py`.
Including `**mixins.DestroyModelMixin**` allows your API to handle DELETE requests, enabling users to delete tags.

Here's the updated **`TagViewSet`** implementation:

```python
#recipe\views.py
                 
class TagViewSet(mixins.DestroyModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet): # need later optimize
    """Manage tags in the database."""
    ...

```

**Key Points**

- By adding `**mixins.DestroyModelMixin**`, the **`TagViewSet`** now supports DELETE requests. This mixin provides
the `**.destroy()**` action which is invoked when a DELETE request is made.
- The existing **`ListModelMixin`** and **`UpdateModelMixin`** are retained to continue supporting
listing and updating tags.
- The **get_queryset** method is kept as is, ensuring that users can only interact with their own tags.
- Make sure that your authentication and permission classes (e.g., TokenAuthentication and IsAuthenticated)
are correctly set to protect your API endpoints.

With these changes, your Tags API will now support deleting tags, allowing users to manage their tags more
effectively. After making these updates, test your API to ensure that the delete functionality is working correctly
and that tags can be securely removed by authorized users.