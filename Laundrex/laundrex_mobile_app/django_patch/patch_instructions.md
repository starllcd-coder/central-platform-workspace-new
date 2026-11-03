# Django patch instructions

## 1) Add apps to `INSTALLED_APPS`
```python
"rest_framework",
"rest_framework_simplejwt",
"apps.mobile_api",
```

## 2) Add REST framework config near the bottom of `laundrex/settings.py`
```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}
```

## 3) Add API routes to `laundrex/urls.py`
```python
path("api/", include("apps.mobile_api.urls")),
```

## 4) Install packages
```bash
pip install djangorestframework djangorestframework-simplejwt
```

## 5) Migrate
```bash
python manage.py migrate
```
```
If migration resolution complains, run:
```bash
python manage.py makemigrations mobile_api
python manage.py migrate
```

## 6) New endpoints added by latest mobile improvements
- `POST /api/devices`
- `POST /api/orders/{id}/bank-transfer-proof`
