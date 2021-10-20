import datetime
import requests
from pprint import pprint


class PhotoBackup:
    url = 'https://api.vk.com/method/'

    def __init__(self, user_id, vk_token):
        self.id = user_id
        self.vk_token = vk_token

    def backup(self):
        file_list = self.vk_get_photos()['response']['items']
        # pprint(file_list)
        files_for_backup = {}
        for photo in file_list:
            # pprint(photo)
            if photo['likes']['count'] in files_for_backup:
                timestamp = photo['date']
                date = (datetime.datetime.fromtimestamp(timestamp)).strftime('%Y-%m-%d')
                name = str(photo['likes']['count']) + '_' + date
            else:
                name = photo['likes']['count']
            max_size_url = photo['sizes'][-1]['url']
            height = photo['sizes'][-1]['height']
            width = photo['sizes'][-1]['width']
            files_for_backup[name] = {
                'max_size_url': max_size_url,
                'size': f'{height}x{width}'
            }

        response = files_for_backup
        return response

    def vk_get_photos(self):
        vk_api_version = '5.131'
        get_photos_url = self.url + 'photos.get/'
        params = {
            'owner_id': self.id,
            'access_token': self.vk_token,
            'v': vk_api_version,
            'album_id': 'profile',
            'extended': 1
        }
        response = requests.get(get_photos_url, params=params)
        return response.json()

    def yandex_upload(self, path_to_file, file_name):
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(ya_token)}
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {
            "path": path_to_file,
            "overwrite": "true"
        }
        response = requests.get(url=upload_url, headers=headers, params=params)
        href = response.json()['href']
        response = requests.put(href, data=open(file_name, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print("Success")


if __name__ == '__main__':
    vk_token = '9b1eb309d15d58b19d06f4808e0ab42bef5fa1bdec1032e442cc7e6979148aa9c444e043e856b75e389b3'
    ya_token = 'AQAAAAARW52bAADLWynE0230hkBqpfooMmOJziU'
    vk_id = '139122829'
    vk_photos = PhotoBackup(vk_id, vk_token)
    # pprint(vk_photos.vk_get_photos())
    pprint(vk_photos.backup())
