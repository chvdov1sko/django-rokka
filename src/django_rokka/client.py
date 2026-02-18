import requests


class RokkaApiClient():
    def __init__(self, api_key):
        self.headers = {
            'Api-Key': api_key,
            'Api-Version': '1',
        }

    def create_source_image(self, organization, filedata):
        url = f'https://api.rokka.io/sourceimages/{organization}'

        try:
            if hasattr(filedata, 'seek'):
                filedata.seek(0)
            response = requests.post(
                url,
                headers=self.headers,
                files={'file': filedata}
            )
        except Exception as e:
            raise ValueError(f"Failed to upload image to rokka: {e}")
        
        if response.status_code != 200:
            raise ValueError(f"Failed to upload image to rokka: {response.text.message}")
        
        data = response.json()
        return data['items'][0]
    
    def delete_source_image(self, organization, img_name):
        img_hash = img_name.split(".")[0]

        url = f'https://api.rokka.io/sourceimages/{organization}/{img_hash}'

        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'

        try:
            response = requests.delete(url, headers=headers)
        except Exception as e:
            raise ValueError(f"Failed to delete image from rokka: {e}")
        
        if response.status_code != 204:
            raise ValueError(f"Failed to delete image from rokka: {response.text.message}")
        
    def get_source_image(self, organization, img_name):
        img_hash = img_name.split(".")[0]

        url = f'https://api.rokka.io/sourceimages/{organization}/{img_hash}'

        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'

        try:
            response = requests.get(url, headers=headers)
        except Exception as e:
            raise ValueError(f"Failed to get image meta from rokka: {e}")
        
        if response.status_code != 200:
            raise ValueError(f"Failed to get image meta from rokka: {response.text.message}")
        
        return response.json()
        