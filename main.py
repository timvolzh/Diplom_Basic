import datetime
import requests
from pprint import pprint
import json
from progress.bar import IncrementalBar
import webbrowser


class PhotoBackup:

    def __init__(self, user_id, ya_token):
        self.id = user_id
        # self.vk_token = vk_token
        self.ya_token = ya_token

    def backup(self):
        global_bar = IncrementalBar('Progress', max=4) # 4- _vk_get_photos, формирование files_for_backup, _yandex_upload, сериализация json_response
        file_list = self._vk_get_photos()['response']['items']
        global_bar.next()
        # pprint(file_list)
        files_for_backup = {}
        json_response = []
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
                'url': max_size_url,
                'size': f'{height}x{width}'
            }
            json_response.append({"file_name": name, "size": f'{height}x{width}'})
        global_bar.next()
        self._yandex_upload(files_for_backup)
        global_bar.next()
        with open("data_file.json", "w") as write_file:
            json.dump(json_response, write_file)
        global_bar.next()
        global_bar.finish()
        return webbrowser.open_new_tab('https://disk.yandex.ru/client/disk/Photo_backup')

    def _vk_get_photos(self):
        vk_url = 'https://api.vk.com/method/'
        vk_token = '9b1eb309d15d58b19d06f4808e0ab42bef5fa1bdec1032e442cc7e6979148aa9c444e043e856b75e389b3'
        vk_api_version = '5.131'
        get_photos_url = vk_url + 'photos.get/'
        params = {
            'owner_id': self.id,
            'access_token': vk_token,
            'v': vk_api_version,
            'album_id': 'profile',
            'extended': 1
        }
        response = requests.get(get_photos_url, params=params)
        return response.json()

    def _yandex_upload(self, files_for_backup):
        upload_bar = IncrementalBar('Uploading photos', max=len(files_for_backup.items()))
        for file in files_for_backup.items():
            # pprint(file)
            path_to_file = f'Photo_backup/{file[0]}'
            file_url = file[1]['url']
            headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(ya_token)}
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            params = {
                "path": path_to_file,
                'url': file_url
            }
            upload = requests.post(url=upload_url, headers=headers, params=params)
            upload.raise_for_status()
            if upload.status_code != 202:
                return 'Failed'
            upload_bar.next()
        upload_bar.finish()
        return "Success"


if __name__ == '__main__':
    ya_token = 'AQAAAAARW52bAADLWynE0230hkBqpfooMmOJziU'
    vk_id = '139122829'
    vk_photos = PhotoBackup(vk_id, ya_token)
    pprint(vk_photos.backup())
