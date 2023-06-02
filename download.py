import bs4
import requests
import json
import urllib.parse
import os

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Origin": "https://podcasts.apple.com",
    "Referer": "https://podcasts.apple.com/",
    "Authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNSRjVITkJHUFEifQ.eyJpc3MiOiI4Q1UyNk1LTFM0IiwiaWF0IjoxNjc5MzU2Nzk0LCJleHAiOjE2ODY2MTQzOTQsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ.7-bg4BXEGfvtQMqhNs2oNqSW_fDoTr6HH1rqKv0o7ORj-6Pwmt4cqdhaEe0uxwmyvPXRaO-aOei6QdW6oX-lzw"
}

def get_metadata(url):
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    parent_data = json.loads(soup.select('#shoebox-media-api-cache-amp-podcasts')[0].getText())
    first_data = json.loads(parent_data[list(parent_data.keys())[0]])
    api_href = first_data['d'][0]['relationships']['episodes']['href']
    # print(api_href)

    # decode uri from soup.select('meta[name="web-experience-app/config/environment"]')[0].attrs['content'] and store to json

    enviroment_data = json.loads(urllib.parse.unquote(soup.select('meta[name="web-experience-app/config/environment"]')[0].attrs['content']))
    api_base = enviroment_data['API']['PodcastHost']
    api_token = enviroment_data['MEDIA_API']['token']
    # print(api_base)
    # print(api_token)
    api_url = api_base + api_href
    while True:
        res = requests.get(api_url, headers=headers)
        res.raise_for_status()
        data = res.json()
        for episode_data in data['data']:
            yield episode_data
        api_href = data.get('next')
        if not api_href:
            break
        api_url = api_base + api_href

def download(episode_data, store_path):
    print(f'Downloading file: {episode_data["attributes"]["name"]}')
    res = requests.get(episode_data['attributes']['assetUrl'])
    res.raise_for_status()
    # filter out illegal path character
    filename = episode_data['attributes']['name'].replace('/', '／').replace('\\', '＼').replace(':', '：').replace('*', '＊').replace('?', '？').replace('"', '＂').replace('<', '＜').replace('>', '＞').replace('|', '｜')[:80]
    with open(os.path.join(store_path, filename + '.mp3'), 'wb') as f:
        for chunk in res.iter_content(100000):
            f.write(chunk)
    with open(os.path.join(store_path, filename + '.json'), 'w', encoding='utf-8') as f:
        json.dump(episode_data, f, indent=4, ensure_ascii=False)

def main():
    download_flag = False
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    for podcast in config['podcasts']:
        store_path = podcast['store_path']
        if not os.path.exists(store_path):
            os.makedirs(store_path)
        for episode_data in get_metadata(podcast['url']):
            season = episode_data['attributes']['seasonNumber']
            episode = episode_data['attributes']['episodeNumber']
            if str(season) in podcast['seasons'].keys() or podcast['save_all_seasons']:
                if not str(season) in podcast['seasons'].keys():
                    podcast['seasons'][str(season)] = {'last_episode': 0}
                if episode > podcast['seasons'][str(season)]['last_episode']:
                    download_flag = True
                    print(f"Downloading season {episode_data['attributes']['seasonNumber']} episode {episode_data['attributes']['episodeNumber']}: {episode_data['attributes']['name']}")
                    podcast['seasons'][str(season)]['tmp_last_episode'] = max(episode, podcast['seasons'][str(season)].get('tmp_last_episode', 0))
                    download(episode_data, store_path)
        for season_key in podcast['seasons']:
            if 'tmp_last_episode' in podcast['seasons'][season_key]:
                podcast['seasons'][season_key]['last_episode'] = podcast['seasons'][season_key]['tmp_last_episode']
                del podcast['seasons'][season_key]['tmp_last_episode']
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    if not download_flag:
        print('everything is up to date')

if __name__ == '__main__':
    main()