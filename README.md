# django-rokka

Django `ImageField` backed by [Rokka.io](https://rokka.io/).

Automatically uploads images to Rokka on save, deletes them when a model is deleted or its
image field is replaced, and gives you stack-aware image URLs.

## Installation

```bash
pip install django-rokka
```

## Setup

```python
# settings.py
INSTALLED_APPS = [
    ...
    "django_rokka",
]

ROKKA_API_KEY = "your-api-key"
ROKKA_ORGANIZATION = "your-organization"
ROKKA_DEFAULT_STACK = "dynamic/noop"  # optional, defaults to "dynamic/noop"
```

## Usage

```python
from django_rokka.fields import RokkaImageField

class Article(models.Model):
    title = models.CharField(max_length=200)
    cover = RokkaImageField()
```

### URLs

```python
# Default stack URL (uses ROKKA_DEFAULT_STACK from settings)
article.cover.url

# Specific Rokka stack
article.cover.stack_url("thumbnail")
article.cover.stack_url("hero--large")
```

URLs resolve to `https://<organization>.rokka.io/<stack>/<hash>.<format>`.

## Migrating existing images

If you are replacing an existing `ImageField` with `RokkaImageField` on a project that already
has images, run the management command. 
It reads images from your current storage (local, S3, GCS, etc.) and uploads them to Rokka, then updates each
DB record. Already migrated images are detected and skipped, so the command is safe
to re-run.

```bash
python manage.py migrate_images_to_rokka
```
