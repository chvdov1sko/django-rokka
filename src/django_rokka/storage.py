import tempfile
import os

from django.conf import settings
from django.core.files.storage import Storage
from rokka_client_codegen import Configuration, ApiClient, SourceimagesApi


class RokkaStorage(Storage):
    def __init__(self):
        api_key = getattr(settings, "ROKKA_API_KEY", None)
        if not api_key:
            raise ValueError("ROKKA_API_KEY is not set in Django settings.")

        org = getattr(settings, "ROKKA_ORGANIZATION", None)
        if not org:
            raise ValueError("ROKKA_ORGANIZATION is not set in Django settings.")

        configuration = Configuration()
        configuration.api_key["api-key"] = api_key

        self.client = SourceimagesApi(ApiClient(configuration))
        self.organization = org
        self.default_stack = getattr(settings, "ROKKA_DEFAULT_STACK", "dynamic/noop")

    def _save(self, name, content):
        try:
            content.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(name)[1]) as tmp:
                for chunk in content.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            response = self.client.create_source_image(
                self.organization, filedata=tmp_path
            )
            file = response.items[0]
            return f"{file.hash}.{file.format}"
        except Exception as e:
            raise ValueError(f"Failed to upload image to rokka: {e}")

    def exists(self, name):
        return False

    def url(self, name, stack = None):
        if not stack:
            stack = self.default_stack
        return f"https://{self.organization}.rokka.io/{stack}/{name}"

    def delete(self, name):
        try:
            # Rokka expects hash only, without file format
            img_hash = name.split(".")[0]
            self.client.delete_source_image(self.organization, img_hash)
        except Exception as e:
            raise ValueError(f"Failed to delete image from rokka: {e}")
        
    def _open(self, name, mode='rb'):
        """Required if you ever call .open() on the field (e.g. for re-processing)."""
        import urllib.request
        url = self.url(name)
        response = urllib.request.urlopen(url)
        from django.core.files.base import ContentFile
        return ContentFile(response.read(), name=name)

    def size(self, name):
        """Called by Django admin and some form validators."""
        # Rokka doesn't expose this easily without fetching the image,
        # so either fetch it or raise NotImplementedError to skip gracefully
        raise NotImplementedError("Size is not supported for Rokka storage")

    def get_available_name(self, name, max_length=None):
        """
        Since Rokka uses content-addressed hashes, collisions are impossible.
        Skip Django's default collision-avoidance logic (which calls exists() in a loop).
        """
        return name
