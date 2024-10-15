import random
import pytest
import requests


class URL:
    BASE_URL_YANDEX = 'https://cloud-api.yandex.net'
    BASE_URL_BREAD = 'https://dog.ceo/api/breed'


class YaUploader:
    def __init__(self):
        self.token = 'OAuth y0_AgAAAAAEoJcvAADLWwAAAAEUcFM2AADV28-PUSxFx6JhBrgbi2X5wF6y_w'
        self.base_url = URL()
        pass

    def create_folder(self, path):
        url_create = f'{self.base_url.BASE_URL_YANDEX}/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': self.token}
        requests.put(f'{url_create}?path={path}', headers=headers)

    def upload_photos_to_yd(self, path, url_file, name):
        url = f"{self.base_url.BASE_URL_YANDEX}/v1/disk/resources/upload"
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': self.token}
        params = {"path": f'/{path}/{name}', 'url': url_file}
        requests.post(url, headers=headers, params=params)

    def get_folder(self):
        url_create = f'{self.base_url.BASE_URL_YANDEX}/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': self.token}
        return requests.get(f'{url_create}?path=/test_folder', headers=headers)

    def delete_folder(self, path):
        url = f'{self.base_url.BASE_URL_YANDEX}/v1/disk/resources'
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
                   'Authorization': self.token}
        requests.delete(f'{url}?path=/{path}', headers=headers)


base_url = URL()


def get_sub_breeds(breed):
    res = requests.get(f'{base_url.BASE_URL_BREAD}/{breed}/list')
    return res.json().get('message', [])


def get_urls(breed, sub_breeds):
    url_images = []
    if sub_breeds:
        for sub_breed in sub_breeds:
            res = requests.get(f"{base_url.BASE_URL_BREAD}/{breed}/{sub_breed}/images/random")
            sub_breed_urls = res.json().get('message')
            url_images.append(sub_breed_urls)
    else:
        url_images.append(requests.get(f"{base_url.BASE_URL_BREAD}/{breed}/images/random").json().get('message'))
    return url_images


def u(breed):
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader()
    yandex_client.delete_folder('test_folder')
    yandex_client.create_folder('test_folder')
    for url in urls:
        part_name = url.split('/')
        name = '_'.join([part_name[-2], part_name[-1]])
        yandex_client.upload_photos_to_yd("test_folder", url, name)


@pytest.mark.parametrize('breed', ['doberman', random.choice(['bulldog', 'spaniel'])])
def test_proverka_upload_dog(breed):
    u(breed)
    yandex_client = YaUploader()
    # проверка
    response = yandex_client.get_folder()
    assert response.status_code == 200, f'Ошибка! Код ответа {response.status_code}. Тело ответа: {response.json()}'
    assert response.json() == "dir"
    assert response.json()['name'] == "test_folder"
    if not get_sub_breeds(breed):
        assert len(response.json()['_embedded']['items']) == 1
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)

    else:
        assert len(response.json()['_embedded']['items']) == len(get_sub_breeds(breed))
        for item in response.json()['_embedded']['items']:
            assert item['type'] == 'file'
            assert item['name'].startswith(breed)
