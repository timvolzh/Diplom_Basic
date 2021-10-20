import requests
import json
from pprint import pprint


class VkBackup:

    def __init__(self,user_id, token, api_version):
        self.id = user_id
        self.token = token
        self.api_version = api_version

    def get_photos(self):
        url = 'https://api.vk.com/method/photos.get/'
        params = {
            'owner_id': self.id,
            'access_token': self.token,
            'v': self.api_version,
            'album_id': 'profile'
        }
        response = requests.get(url, params=params)
        return response.json()







if __name__ == '__main__':
    vk_token = '9b1eb309d15d58b19d06f4808e0ab42bef5fa1bdec1032e442cc7e6979148aa9c444e043e856b75e389b3'
    user_id = '139122829'
    version = '5.131'
    vk_photos = VkBackup(user_id, vk_token, version)
    pprint(vk_photos.get_photos())
