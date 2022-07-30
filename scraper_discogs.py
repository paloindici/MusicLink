import requests
from bs4 import BeautifulSoup


def get_thumb(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    first_filter = soup.find_all('div', {"class": "image_3rzgk bezel_2NSgk"})
    print(first_filter)
    if len(first_filter) == 0:
        return None
    image = first_filter[0].findAll('img')
    if len(image) == 0:
        return None
    if image[0]['src'][:22] != "https://i.discogs.com/":
        return None
    return image[0]['src']

