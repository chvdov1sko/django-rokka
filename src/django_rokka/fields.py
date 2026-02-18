from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.db.models.signals import post_delete, pre_save

from django_rokka.storage import RokkaStorage


class RokkaImageFieldFile(ImageFieldFile):
    @property
    def url(self):
        if not self.name:
            return None
        return self.storage.url(self.name)

    def stack_url(self, stack):
        if not self.name:
            return None
        return self.storage.url(self.name, stack)


class RokkaImageField(ImageField):
    attr_class = RokkaImageFieldFile

    def __init__(self, *args, **kwargs):
        kwargs['storage'] = RokkaStorage()
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        # Attach signals to model
        post_delete.connect(self._post_delete, sender=cls)
        pre_save.connect(self._pre_save, sender=cls)

    def _post_delete(self, sender, instance, **kwargs):
        field_file = getattr(instance, self.attname)
        if field_file and field_file.name:
            field_file.storage.delete(field_file.name)

    def _pre_save(self, sender, instance, **kwargs):
        """
        Delete old image from Rokka when field is replaced or cleared
        """
        if not instance.pk:
            return

        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return

        old_file = getattr(old_instance, self.attname)
        new_file = getattr(instance, self.attname)

        old_name = old_file.name if old_file else None
        new_name = new_file.name if new_file else None

        if old_name and old_name != new_name:
            old_file.storage.delete(old_name)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop('storage', None)
        return name, path, args, kwargs