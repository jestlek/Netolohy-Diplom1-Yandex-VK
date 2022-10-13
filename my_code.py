import requests
import json
from datetime import datetime
import os

with open('token.txt', 'w') as f:
    token = str(input('Введите токен VK: ').strip())
    f.write(token)

my_list = []
photos_info = []

def _download_json_photos(user_id=None, count=None):
    URL = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': user_id,
        'access_token': token,
        'v': '5.131',
        'album_id': 'profile',
        'count': count,
        'extended': 'extended=1',
        'photo_sizes': 'photo_sizes=1'
    }
    res = requests.get(URL, params=params)
    with open('photos.json', 'w') as f:
        json.dump(res.json(), f, ensure_ascii=False, indent=2)

def _high_photos():
    with open('photos.json', 'r') as f:
        data = json.load(f)
    for photo in data['response']['items']:
        info = {
            'file_name': str(photo['likes']['count']) + '_' + str(datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')) + '.jpg',
            'url': photo['sizes'][-1]['url']
        }
        my_list.append(info)
        info2 = {
            'file_name': str(photo['likes']['count']) + '_' + str(datetime.utcfromtimestamp(photo['date']).strftime('%Y-%m-%d')) + '.jpg',
            'size': photo['sizes'][-1]['type']
        }
        photos_info.append(info2)
    print(f'{"." * 8}Инициализирован список фотографий из профиля')


def download_photos():
    _download_json_photos(user_id=input('Введите ID пользователя VK: '), count=input('Сколько фотографий скачать? '))
    _high_photos()
    if not os.path.exists(os.getcwd() + '/download_photos'):
        os.mkdir('download_photos')
    count = 0
    for photo in my_list:
        with open(f'download_photos/{photo["file_name"]}', 'wb') as picture:
            image = requests.get(photo['url'])
            picture.write(image.content)
        count += 1
        print(f'{"." * 6}Фото №{count} успешно загружено')
    with open('download_photos/photos_info.json', 'w') as f:
        json.dump(photos_info, f, ensure_ascii=False, indent=2)
    print(f'Было загружено {count} фото и json файл с информацией в папку /download_photos')

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def _upload_link(self, file_path: str):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': file_path, 'owerwrite': 'true'}
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def _create_folder(self, file_path: str):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        requests.put(url + '?path=' + file_path, headers=headers)

    def upload(self, file_path):
        self._create_folder('download_photos')
        count = 0
        for photo in photos_info:
            link_dict = self._upload_link(file_path + '/' + photo['file_name'])
            href = link_dict['href']
            response = requests.put(href, data=open(f'download_photos/{photo["file_name"]}', 'rb'))
            response.raise_for_status()
            count += 1
            if response.status_code == 201:
                print(f'...Фото №{count} загружено')
        print(f'Было загружено {count} фото на Яндекс Диск')


if __name__ == '__main__':
    download_photos()
    token = input('Введите token Yandex: ')
    uploader = YaUploader(token)
    result = uploader.upload('download_photos')
