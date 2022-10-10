from os import getcwd, mkdir, system
from requests import codes, get, status_codes
from time import localtime

from bs4 import BeautifulSoup
from cv2 import getTickCount, getTickFrequency
import pandas as pd


def display_datetime():
    y,m,d,h,m,s = localtime()[:6]
    current_date = str(y)+'Y'+str(m)+'M'+str(d)+'D'+str(h)+'H'+str(m)+'M'+str(s)+'S'
    return current_date


def collect_winery_information(soup):
    # Collecting winery name
    winery_name, website_link = '', ''

    find_winery_name = soup.find('h2')
    winery_name = find_winery_name.string.split(': ')[-1]

    # Collect winery url
    find_winery_url = soup.find_all('i')
    for things in find_winery_url:
        try:
            if 'Web site:' in things:
                website_link = things.next_sibling.next_sibling
                website_link = website_link.get('href').rstrip('/')
        except AttributeError:
            website_link = ''
    
    return winery_name.strip(), website_link.strip()


def collect_social_media_information(soup):
    # Collecting social media links
    twitter_id, facebook_id, instagram_id, youtube_id = '', '', '', ''
    social_media_links = soup.find_all('a')

    for link in social_media_links:
        if 'www.twitter.com' in link.get('href'):
            twitter_id = link.get('href').strip()
            break

    for link in social_media_links:
        if 'www.facebook.com' in link.get('href'):
            facebook_id = link.get('href').strip()
            break

    for link in social_media_links:
        if 'www.instagram.com' in link.get('href'):
            instagram_id = link.get('href').strip()
            break

    for link in social_media_links:
        if 'www.youtube.com' in link.get('href'):
            youtube_id = link.get('href').strip()
            break

    return twitter_id.strip(), facebook_id.strip(), instagram_id.strip(), youtube_id.strip()


def write_to_csv(name, link, twitter, facebook, instagram, youtube):
    with open(f'{pwd}dataset/raw/raw.csv', 'a') as f:
        f.write(f'{name},{link},{twitter},{facebook},{instagram},{youtube}\n')


def write_to_xlsx(name, link, twitter, facebook, instagram, youtube):
    with open(f'{pwd}dataset/raw/raw.xlsx', 'a') as f:
        f.write(f'{name},{link},{twitter},{facebook},{instagram},{youtube}\n')


# Print end date/time
print(f'Program start at {display_datetime()}')

# Start program timer
start_timer = getTickCount()


# Variables to be used
pwd = getcwd() + '/'
winerelease_url = r'https://www.winerelease.com/Winery_List/Alphabetical_Winery_List.html'
winerelease_base = r'https://www.WineRelease.com/WineryInfo/'


# Create file structure
try: mkdir(f'{pwd}dataset/')
except FileExistsError: pass
try: mkdir(f'{pwd}dataset/backup')
except FileExistsError: pass
try: mkdir(f'{pwd}dataset/raw')
except FileExistsError: pass


# Create csv and xlsx file before beginning
with open('dataset/raw/raw.csv', 'w') as f:
    f.write('winery_name,winery_location,twitter_url,facebook_url,instagram_url,youtube_url\n')

with open('dataset/raw/raw.xlsx', 'w') as f:
    f.write('winery_name,winery_location,twitter_url,facebook_url,instagram_url,youtube_url\n')


# navigate to winerelease.com
resp = get(winerelease_url)

if resp.status_code != codes.OK:
    print(f'{winerelease_url} could not be reached >> status code: {resp.status_code}')
    quit()


# gather ALL winery links from body into a list
soup = BeautifulSoup(resp.text, 'lxml')

table_body = soup.find('ul')

url_list = []
for link in table_body.find_all('a'):
    if not link.get('href').endswith('.html'):
        continue
    url_list.append(link.get('href').split('/')[-1])


# Use winery links in list and parse each page
for winery in url_list:
    resp_search = get(winerelease_base + winery)

    if resp_search.status_code == codes.OK:
        soup_search = BeautifulSoup(resp_search.text, 'lxml')
        
        # Collect basic winery information
        winery, website = collect_winery_information(soup_search)

        # Collect social media links
        twitter, facebook, instagram, youtube = collect_social_media_information(soup_search)

        # Write csv dataset
        write_to_csv(winery, website, twitter, facebook, instagram, youtube)
        
        # Write xlsx dataset
        write_to_xlsx(winery, website, twitter, facebook, instagram, youtube)


# Create a backup of datasets
system(f'cp "{pwd}dataset/raw/raw.csv" "{pwd}dataset/backup/raw.csv"')
system(f'cp "{pwd}dataset/raw/raw.xlsx" "{pwd}dataset/backup/raw.xlsx"')


# Print end date/time
print(f'Program ended at {display_datetime()}')

# Display timer
end_timer = getTickCount()
completion_time = (end_timer - start_timer)/getTickFrequency()
print(f'Program took {completion_time/60} minutes to complete.')    