[ <-- 5. Setup Django Admin ](Setup%20Django%20Admin.md)
# 5. Api Documentation

___
## Step 1. Install drf-spectacular

drf-spectacular is an extension for Django REST Framework (DRF) that provides automatic schema generation for APIs
in the OpenAPI 3.0 format. This extension helps in creating documentation for APIs implemented using DRF, doing so
automatically and with high accuracy. 

Update _**requirements.txt**_:
```text
drf-spectacular>=0.15.1,<0.16
```
add in **_settings.py_**:
```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'COMPONENT_SPLIT_REQUEST': True,
}
```

## Step 2. Configure URLs

In app>app>urls.py update next:

```python
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
urlpatterns = [
    ...
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'),
         name='api-docs',),
    ]
```
Open:
http://127.0.0.1:8000/api/docs/

*img.

____
> **Commits:**
>
> https://github.com/stupns/recipe-app-api/commit/dc6f40b
