# django-rokka

Django `ImageField` backed by [Rokka.io](https://rokka.io/) — an image processing and CDN service.

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
has images, run the management command **before** switching your storage backend. It reads images
from your current storage (local, S3, GCS, etc.) and uploads them to Rokka, then updates each
DB record in place. Already-migrated images are detected and skipped, so the command is safe
to re-run.

```bash
python manage.py migrate_images_to_rokka
```

### Order of operations

1. Install the package and replace `ImageField` → `RokkaImageField` in your models
2. Run Django migrations
3. Run `migrate_images_to_rokka` while your old storage backend is still configured
4. Verify images are accessible, then optionally remove the old storage configuration

## Configuration reference

| Setting | Required | Default | Description |
|---|---|---|---|
| `ROKKA_API_KEY` | ✓ | — | Your Rokka API key |
| `ROKKA_ORGANIZATION` | ✓ | — | Your Rokka organization name |
| `ROKKA_DEFAULT_STACK` | | `dynamic/noop` | Stack used for `.url` property |

## Error reference

All errors are importable from `django_rokka.errors`.

| Exception | Raised when |
|---|---|
| `RokkaConfigError` | `ROKKA_API_KEY` or `ROKKA_ORGANIZATION` is missing |
| `RokkaImageUploadError` | Upload to Rokka fails |
| `RokkaImageDeleteError` | Delete from Rokka fails |
| `RokkaImageNotFoundError` | Image does not exist in Rokka |