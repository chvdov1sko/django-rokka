from django.conf import settings
from django.core.files.storage import Storage
from django_rokka.client import RokkaApiClient


class RokkaStorage(Storage):
    def __init__(self):
        api_key = getattr(settings, "ROKKA_API_KEY", None)
        if not api_key:
            raise ValueError("ROKKA_API_KEY is not set in Django settings.")

        rokka_organization = getattr(settings, "ROKKA_ORGANIZATION", None)
        if not rokka_organization:
            raise ValueError("ROKKA_ORGANIZATION is not set in Django settings.")
        
        self.default_stack = getattr(settings, "ROKKA_DEFAULT_STACK", "dynamic/noop")

        self.client = RokkaApiClient(api_key)
        self.organization = rokka_organization

    def _save(self, name, content):
        file = self.client.create_source_image(
            self.organization, filedata=content
        )
        return f"{file['hash']}.{file['format']}"
    
    def delete(self, name):
        if not name:
            return
        self.client.delete_source_image(self.organization, name)

    def url(self, name, stack = None):
        if not stack:
            stack = self.default_stack
        return f"https://{self.organization}.rokka.io/{stack}/{name}"

    def size(self, name):
        return self.client.get_source_image(self.organization, name).size
    
    def width(self, name):
        return self.client.get_source_image(self.organization, name).width
    
    def height(self, name):
        return self.client.get_source_image(self.organization, name).height

    def exists(self, name):
        return False