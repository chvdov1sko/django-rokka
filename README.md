# django-rokka-field

Django `ImageField` backed by [Rokka.io](https://rokka.io/).

Automatically uploads images to Rokka on save, deletes them on model delete or field replace,
and gives you stack-aware URLs.

## Installation
```bash
pip install django-rokka-field
```

Or directly from GitLab:
```bash
pip install git+https://gitlab.com/yourname/django-rokka-field.git
```

## Setup
```python
# settings.py
INSTALLED_APPS = [
    ...
    "rokka_field",
]

ROKKA_API_KEY = "your-api-key"
ROKKA_ORGANIZATION = "your-organization"
ROKKA_DEFAULT_STACK = "dynamic/noop"  # optional, this is the default
```

## Usage
```python
from rokka_field import RokkaImageField

class Article(models.Model):
    title = models.CharField(max_length=200)
    cover = RokkaImageField()
```
```python
# default stack URL
article.cover.url

# specific Rokka stack
article.cover.stack_url("thumbnail")
article.cover.stack_url("hero--large")
```

## Behavior

- **Upload** — image is uploaded to Rokka on `instance.save()`, the Rokka hash is stored in the DB
- **Replace** — old image is deleted from Rokka automatically when a new one is saved
- **Delete** — image is deleted from Rokka when the model instance is deleted
```

---

**`.gitignore`**
```
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.env
.venv/