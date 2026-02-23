import requests

from django_rokka.errors import RokkaError, RokkaConfigError, RokkaInvalidImageNameError
from django_rokka.helpers import is_rokka_name

class RokkaApiClient():
    def __init__(self, api_key):
        if not api_key:
            raise RokkaConfigError("Api key is required to use RokkaApiClient.")

        self.headers = {
            'Api-Key': api_key,
            'Api-Version': '1',
        }
        self.base_url = 'https://api.rokka.io/sourceimages'

    def create_source_image(self, organization, filedata):
        """
        Uploads an image to Rokka. Returns dict with image metadata on success.
        Throws RokkaError on any error.
        """
        url = f'{self.base_url}/{organization}'

        try:
            if hasattr(filedata, 'seek'):
                filedata.seek(0)
            response = requests.post(
                url,
                headers=self.headers,
                files={'file': filedata}
            )
        except Exception as e:
            raise RokkaError(f"Failed to upload image to rokka: {e}")
        
        if response.status_code != 200:
            message = response.json().get('message', response.text)
            raise RokkaError(f"Failed to upload image to rokka: {message}")
        
        items = response.json().get('items')

        if not items:
            raise RokkaError("Rokka upload response missing items.")

        return items[0]
    
    def delete_source_image(self, organization, img_name):
        """
        Deletes a source image from Rokka. Extracts hash from img_name.
        Throws RokkaInvalidImageNameError if image name is invalid.
        Throws RokkaError on any other error.
        """
        if not is_rokka_name(img_name):
            raise RokkaInvalidImageNameError(f"Invalid Rokka image name: {img_name}")

        img_hash = img_name.split(".")[0]

        url = f'{self.base_url}/{organization}/{img_hash}'

        try:
            response = requests.delete(url, headers=self.headers)
        except Exception as e:
            raise RokkaError(f"Failed to delete image from rokka: {e}")
        
        if response.status_code != 204:
            message = response.json().get('message', response.text)
            raise RokkaError(f"Failed to delete image from rokka: {message}")
        
    def get_source_image(self, organization, img_name, stack):
        """
        Retrieve a source image from Rokka. Exctracts hash from img_name.
        Throws RokkaInvalidImageNameError if image name is invalid.
        Throws RokkaError on any other error.
        """
        if not is_rokka_name(img_name):
            raise RokkaInvalidImageNameError(f"Invalid Rokka image name: {img_name}")

        url = f"https://{organization}.rokka.io/{stack}/{img_name}"

        try:
            response = requests.get(url, headers=self.headers)
        except Exception as e:
            raise RokkaError(f"Failed to get image from rokka: {e}")
        
        if response.status_code != 200:
            message = response.json().get('message', response.text)
            raise RokkaError(f"Failed to get image from rokka: {message}")
        
        return response.content
        
    def get_source_image_meta(self, organization, img_name):
        """
        Retrieve metadata for a source image from Rokka. Exctracts hash from img_name.
        Throws RokkaInvalidImageNameError if image name is invalid.
        Throws RokkaError on any other error.
        """
        if not is_rokka_name(img_name):
            raise RokkaInvalidImageNameError(f"Invalid Rokka image name: {img_name}")

        img_hash = img_name.split(".")[0]

        url = f'{self.base_url}/{organization}/{img_hash}'

        try:
            response = requests.get(url, headers=self.headers)
        except Exception as e:
            raise RokkaError(f"Failed to get image meta from rokka: {e}")
        
        if response.status_code != 200:
            message = response.json().get('message', response.text)
            raise RokkaError(f"Failed to get image meta from rokka: {message}")
        
        return response.json()
        