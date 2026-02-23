"""
Find all models with RokkaImageField and uploads any images not yet on Rokka.
Already-migrated images are skipped.

Usage: python manage.py migrate_images_to_rokka
"""
from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from django_rokka.fields import RokkaImageField
from django_rokka.storage import RokkaStorage
from django_rokka.helpers import is_rokka_name


def _find_rokka_fields():
    """
    Return [(ModelClass, field_name), ...] for every RokkaImageField in the project.
    """
    results = []
    for model in apps.get_models():
        for field in model._meta.get_fields():
            if isinstance(field, RokkaImageField):
                results.append((model, field.name))
    return results


class Command(BaseCommand):
    help = ("Migrate existing images to Rokka. Discovers all RokkaImageField fields, downloads each image from its current storage backend, uploads it to Rokka, and updates the DB record.")

    def handle(self, *args, **options):
        rokka_fields = _find_rokka_fields()
        if not rokka_fields:
            self.stdout.write("No RokkaImageFields found in any installed apps.")
            return

        total_migrated = 0
        total_skipped = 0
        total_failed = 0

        for model, field_name in rokka_fields:
            self.stdout.write(f"\n── {model._meta.app_label}.{model.__name__}.{field_name}")

            migrated, skipped, failed = self._migrate_field(model, field_name)
            total_migrated += migrated
            total_skipped += skipped
            total_failed += failed

        self.stdout.write("\n" + "─" * 50)
        self.stdout.write(
            f"Done.  "
            f"Migrated: {self.style.SUCCESS(str(total_migrated))}  "
            f"Skipped: {total_skipped}  "
            f"Failed: {self.style.ERROR(str(total_failed)) if total_failed else '0'}"
        )

    def _migrate_field(self, model: Any, field_name: str) -> tuple[int, int, int]:
        migrated = skipped = failed = 0
        rokka_storage = RokkaStorage()

        qs = model.objects.exclude(**{field_name: ''}).exclude(**{f"{field_name}__isnull": True})
        total = qs.count()

        if total == 0:
            self.stdout.write("No instances with images.")
            return 0, 0, 0

        self.stdout.write(f"{total} image(s) to migrate.")

        for instance in qs.iterator():
            field_file = getattr(instance, field_name)
            current_name: str = field_file.name

            if not current_name:
                skipped += 1
                continue

            if is_rokka_name(current_name):
                self.stdout.write(f"   SKIP     {current_name} (already in Rokka)")
                skipped += 1
                continue

            try:
                with default_storage.open(current_name, 'rb') as file_obj:
                    new_name = rokka_storage._save(current_name, file_obj)

                model.objects.filter(pk=instance.pk).update(**{field_name: new_name})
                self.stdout.write(self.style.SUCCESS(f"   MIGRATE  {current_name} -> {new_name}"))
                migrated += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   FAIL     {current_name}: {e}"))
                failed += 1

        return migrated, skipped, failed