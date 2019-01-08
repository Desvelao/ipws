# -*- coding: utf-8 -*-
# ipws.py Download images from instagram profiles created by Desvelao^^ (iamdesvelao@gmail.com)
# refs https://stackoverflow.com/questions/31784484/how-to-parallelized-file-downloads
# Get Instagram photos: https://www.techuntold.com/view-full-size-instagram-photos/
# Selenium docs: https://selenium-python.readthedocs.io/installation.html#drivers

import asyncio, os, bs4, time, re, argparse
from aiohttp import ClientSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import argparse
import pipreqs

# HOW TO USE
# python3 ipws.py <public instagram profile username> [-c/--croop] [-t/--time <value of [0.25,0.5,1,1.5,2,2.5,3]>]

parser = argparse.ArgumentParser()
parser.add_argument('username', help = 'Instagram Profile Username to get photos')
parser.add_argument("-c", "--croop", action="store_true",
                    help="download reduced size images")
parser.add_argument("-t", "--time", type=int, choices = [0.25,0.5,1,1.5,2,2.5,3],
                    help="set wait time to scrolldown the navigator")
args = parser.parse_args()

#Constants
INSTAGRAM_URL = 'https://www.instagram.com/{}'
INSTAGRAM_URL_PHOTOS = 'https://www.instagram.com/p/{}'
INSTAGRAM_URL_PHOTOS_ = 'https://www.instagram.com/p/'
TAKEN_BY = '?taken-by='
MEDIA_SIZE_L = 'media/?size=l'
SCROLL_PAUSE_TIME = 0.25 #seconds pause to scrolldown page
photo_id = 0 #filename ordered by num

# print(args)
# if args.verbose:
#     print("the square of {} equals {}".format(args.square, answer))
# else:
#     print(answer)

username = args.username
full_mode = True if not args.croop else False
time_pause =  SCROLL_PAUSE_TIME if not args.time else args.time
print('Instagram PhotoScrapper by Desvelao^^')
print('--------------------------------------')
print(f'Username: {username}\nFullmode: {full_mode}\nTime between gathering url images {time_pause}')
print('--------------------------------------')

#Backup folder
backup_folder = 'photos'

#Create a backup folder if not exists
os.makedirs(backup_folder, exist_ok=True)

backup_folder += '/'+username
os.makedirs(backup_folder,exist_ok=True)

img_set = set()

#Create a browser and go to instrgram profile
chrome_options = Options()
chrome_options.add_argument("--headless")

print('Starting...')
browser = webdriver.Chrome(chrome_options = chrome_options) #TODO: headless browser
browser.get(INSTAGRAM_URL.format(username))
print('Scrapping profile...')

# links = browser.find_elements_by_tag_name('a')
# images = list(map(lambda img: img.get_attribute('href').replace(TAKEN_BY+username,MEDIA_SIZE_L),
#         filter(lambda img: img.get_attribute('href').startswith(INSTAGRAM_URL_PHOTOS_),links)))
# for img in images:
#     img_set.add(img)
# print(img_set)
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

# page_source = browser.page_source

#Get elements withs img tags
# img_tags = browser.find_elements_by_tag_name('img')
# page_source = 'dsdsa sdadsa dsa adwa da asda dadwa dsa asd awda src="http://dsada.jpg" src="https://dsada.jpg"'
# findre = re.findall('src="https?:\/\/([^(?!\.jpg")]+\.jpg.?)"',page_source,re.M)
# findre = re.findall('src="https?:\/\/([^"]+)"',page_source,re.M)
# print('FindRe: ' + str(len(findre)))

# with open(backup_folder+'/source.html', "w", encoding = 'utf-8') as f:
#     f.write(page_source)

# print(len(img_tags))
# print(browser.page_source)
# soup = bs4.BeautifulSoup(browser.page_source, 'html5lib') # 'html.parser'
# print(len(soup.find_all('img')))

#Get url images from tags founded
# images = list(map(lambda img: img.get_attribute('src'),
#     filter(lambda img: img.get_attribute('src').endswith('.jpg'),img_tags)))

# print(images)
#Close and exists browser
# browser.quit()

#Define async functions
async def fetch_photo(url,session):
    print(f'Downloading...{url}')
    async with session.get(url) as response:
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
            print(f'Downloaded: {response.url} to {backup_folder + "/" + filename}')

async def get_userphotos(urls):
    async with ClientSession() as session:
        # futures = [await fetch_photo(url,session) for url in urls]
        tasks = [fetch_photo(url,session) for url in urls]
        return await asyncio.gather(*tasks)
        # print(f'\n>> DOWNLOADED: {len(urls)} images')

#Download files
print(f'>> FOUNDED: {len(img_set)} images\n')

loop = asyncio.get_event_loop()
loop.run_until_complete(get_userphotos(img_set))

print(f'\n>> DOWNLOADED: {len(img_set)} images')
print('--------------------------------------')
print('Instagram Photo Web Scrapper (IPWS) by Desvelao^^')
print('--------------------------------------')