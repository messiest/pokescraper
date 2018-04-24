import os
import argparse

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup


DATA_DIR = 'images/'
URL_TEMPLATE = "https://pokemondb.net/sprites/{}"  # .format("bulbasaur")

REJECT = [
    'google-plus.png',
    'facebook.png',
    'message.png',
    'twitter.png'
]


parser = argparse.ArgumentParser()
parser.add_argument(
    'pkmn',
    type=str,
)

def write_to_file(filename, content):
    with open(filename, 'wb') as f:
        f.write(content)


def get_urls(pkmn):
    url = URL_TEMPLATE.format(pkmn)
    html = requests.get(url)
    b = BeautifulSoup(html.text, 'lxml')
    imgs = [img['data-original'] for img in b.findAll('img') if img['data-original'].split('/')[-1] not in REJECT]

    return imgs


def downloader(pkmn, data_dir=DATA_DIR):
    if not os.path.exists(os.path.join(data_dir, pkmn)):
        os.mkdir(os.path.join(data_dir, pkmn))
    urls = get_urls(pkmn.lower())
    pbar = tqdm(urls, desc=pkmn.capitalize())
    for url in pbar:
        # file_name = url.split('/')[-1]
        file_name = '-'.join(url.split('/')[-3:])
        file_path = os.path.join(data_dir, pkmn, file_name)
        try:
            image = requests.get(url, timeout=5)
        except Exception as e:
            tqdm.write("{} | {}".format(str(e.__doc__), url))
            continue

        # error handling
        headers = image.headers
        try:
            if image.status_code != 200:
                tqdm.write("connection error {} | {}".format(image.status_code, url))
                continue
            elif 'back' in file_name:
                tqdm.write("back picture | {}".format(url))
                continue
            elif headers['Content-Type'] != 'image/png':
                tqdm.write("file type error {} | {}".format(headers['Content-Type'], url))
                continue
            elif int(headers['Content-Length']) < 100:  # min file size
                tqdm.write("file size error {} | {}".format(headers['Content-Length'], url))
                continue
            elif pkmn in file_name:
                write_to_file(file_path, image.content)
                pbar.update()
                images += 1
        except:
            continue


if __name__ == "__main__":
    args = parser.parse_args()
    pkmn = args.pkmn

    downloader(pkmn)
