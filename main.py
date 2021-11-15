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

    def backup(self):  # основной метод, вызывающий загрузку фото и формирующий ответ
        global_bar = IncrementalBar('Progress', max=4)
        file_list = self._vk_get_photos()['response']['items']  # получаем список фото из VK
        global_bar.next()
        files_for_backup = {}
        json_response = []
        for photo in file_list:  # формируем список для загруки на Я.Диск, задание имен файлам
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
        self._yandex_upload(files_for_backup)  # отправляем список фото для загрузки на Я.Диск
        global_bar.next()
        with open("data_file.json", "w") as write_file:  # сохраняем файл с результатом
            json.dump(json_response, write_file)
        global_bar.next()
        global_bar.finish()
        return 'Backup finished'

    def _vk_get_photos(self):  # метод получающий список фото из VK
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

    def _yandex_upload(self, files_for_backup):  # метод создающий папку на Я.Диск и загружающий в неё фото
        upload_bar = IncrementalBar('Uploading photos', max=len(files_for_backup.items()))
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(ya_token)}
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        make_dir_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        upload_dir_name = 'Photo_backup'
        requests.put(url=make_dir_url, headers=headers, params={'path': upload_dir_name})
        for file in files_for_backup.items():
            path_to_file = f'{upload_dir_name}/{file[0]}'
            file_url = file[1]['url']
            params = {
                'path': path_to_file,
                'url': file_url
            }
            upload = requests.post(url=upload_url, headers=headers, params=params)
            upload.raise_for_status()
            if upload.status_code != 202:  # проверка на успешность загрузки
                return 'Upload failed'
            upload_bar.next()
        upload_bar.finish()
        return webbrowser.open_new_tab(f'https://disk.yandex.ru/client/disk/{upload_dir_name}')


if __name__ == '__main__':
    ya_token = ''
    vk_id = '139122829'
    vk_photos = PhotoBackup(vk_id, ya_token)
    pprint(vk_photos.backup())
