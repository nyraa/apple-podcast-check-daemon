# apple podcast automatically check&download tool

## usage
Clone or download this repo and rename `config_template.json` to `config.json` and fill the information in to it.  
You can add this script to some schedule programs like Windows Task Scheduler or etc. 

## config file format example
```json
{
    "podcasts": [
        {
            "url": "https://podcasts.apple.com/us/podcast/%E5%BF%B5%E4%BA%86%E5%BF%83%E7%90%86%E5%AD%B8-%E7%84%B6%E5%BE%8C%E5%91%A2/id1616453135",
            "store_path": "store_test",
            "save_all_seasons": true,
            "seasons": {
                "3": {
                    "last_episode": 5
                },
                "2": {
                    "last_episode": 30
                },
                "1": {
                    "last_episode": 30
                }
            }
        }
    ]
}
```
* `url` is the url of that podcast folder
* `store_path` is the path that the files stored
* `save_all_seasons` to download new season that is not listed on the `seasons` and add it to `seasons` automatically
* `seasons` stores the lastest episode information

## requirement
* requests
* beautifulsoup4

```bash
pip install -r requirements.txt
```