# -*- coding: utf-8 -*-
# ipws.py Download images from Instagram public profiles created by Desvelao^^ (iamdesvelao@gmail.com)
# refs https://stackoverflow.com/questions/31784484/how-to-parallelized-file-downloads
# Get Instagram photos: https://www.techuntold.com/view-full-size-instagram-photos/
# Selenium docs: https://selenium-python.readthedocs.io/installation.html#drivers

import asyncio, os, time, re, argparse
from aiohttp import ClientSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import argparse
import pipreqs

# HOW TO USE
# python3 ipws.py <public instagram profile username> [-c/--croop] [-t/--time <value of [0.25,0.5,1,1.5,2,2.5,3]>] [-/f/--folder <folder>]

parser = argparse.ArgumentParser(prog= 'ipws')
parser.add_argument('username', help = 'Instagram Profile Username to get photos')
parser.add_argument('-c', '--croop', action='store_true',
                    help='download reduced size images')
parser.add_argument('-t', '--time', type=float, choices = [0.25,0.5,1,1.5,2,2.5,3],
                    help='set wait time to scrolldown the navigator')

parser.add_argument('-f', '--folder', type=str, help='set destination folder', metavar='folder')

args = parser.parse_args()

#Constants
INSTAGRAM_URL = 'https://www.instagram.com/{}'
INSTAGRAM_URL_PHOTOS = 'https://www.instagram.com/p/{}'
INSTAGRAM_URL_PHOTOS_ = 'https://www.instagram.com/p/'
TAKEN_BY = '?taken-by='
MEDIA_SIZE_L = 'media/?size=l'
SCROLL_PAUSE_TIME = 0.25 #seconds pause to scrolldown page
SEMAPHORE = 1
photo_id = 0 #filename ordered by num

username = args.username
full_mode = True if not args.croop else False
time_pause =  SCROLL_PAUSE_TIME if not args.time else args.time
backup_folder_base = 'photos' if not args.folder else args.folder
backup_folder = backup_folder_base + '/' + username

#Define async functions
async def fetch_photo(url,session):
    print(f'Downloading...{url}')
    async with semaphore, session.get(url) as response:
        print(f'Downloaded...{url}')
        file = await response.read()
        filename =  os.path.basename(str(response.url))
        global photo_id
        if not filename.endswith('.jpg'):
            filename = re.search('(.*\.jpg)',filename)
            if filename:
                filename = filename[1]
            else:
                filename = str(photo_id) + '.jpg'
                photo_id += 1
        with open(backup_folder+'/'+filename, "wb") as f:
            f.write(file)
            print(f'Saved: {response.url} to {backup_folder + "/" + filename}')

async def get_userphotos(urls):
    async with ClientSession() as session:
        # futures = [await fetch_photo(url,session) for url in urls]
        tasks = [fetch_photo(url,session) for url in urls]
        return await asyncio.gather(*tasks)

#Download files
if __name__ == "__main__":
    print('Instagram Photo Web Scraper by Desvelao^^')
    print('--------------------------------------')
    print(f'Username: {username}\nFullmode: {full_mode}\nTime between gathering url images: {time_pause}\nFolder: {backup_folder}')
    print('--------------------------------------')

    #Create a backup folder if not exists
    os.makedirs(backup_folder_base, exist_ok=True)
    
    os.makedirs(backup_folder + '', exist_ok=True)

    img_set = set()

    #Create a browser and go to instagram profile
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    print('Starting...')
    browser = webdriver.Chrome(chrome_options = chrome_options)
    browser.get(INSTAGRAM_URL.format(username))
    print('Scrapping profile...')

    #Semaphore
    semaphore = asyncio.Semaphore(SEMAPHORE)

    # Get scroll height
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(time_pause)
        # Calculate new scroll height and compare with last scroll height
        img_tags = browser.find_elements_by_tag_name('img')
        if full_mode:
            links = browser.find_elements_by_tag_name('a')
            images = list(map(lambda img: img.get_attribute('href') + MEDIA_SIZE_L,
                    filter(lambda img: img.get_attribute('href').startswith(INSTAGRAM_URL_PHOTOS_),links)))
            # images = list(map(lambda img: img.get_attribute('href').replace(TAKEN_BY+username,MEDIA_SIZE_L),
            #         filter(lambda img: img.get_attribute('href').startswith(INSTAGRAM_URL_PHOTOS_),links)))
        else:
            images = list(map(lambda img: img.get_attribute('src'),
            filter(lambda img: img.get_attribute('src').endswith('.jpg'),img_tags)))
        for img in images:
            print(img)
            img_set.add(img)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print('...')
        
    print(f'>> FOUND: {len(img_set)} images\n')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_userphotos(img_set))
    loop.close()

    print(f'\n>> DOWNLOADED: {len(img_set)} images')
    print('--------------------------------------')
    print('Instagram Photo Web Scraper (IPWS) by Desvelao^^')
    print('--------------------------------------')