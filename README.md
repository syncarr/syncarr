# Syncarr
Syncs two Radarr/Sonarr/Lidarr servers through the web API. Useful for syncing a 4k radarr/sonarr instance to a 1080p radarr/sonarr instance.

* Supports Radarr/Sonarr version 2 and 3.
* Can sync by `profile` name or `profile_id`
* Filter what media gets synced by `profile` name or `profile_id`
* Supports Docker for multiple instances
* Can set interval for syncing
* Support two way sync (one way by default)


## Configuration
 1. Edit the config.conf file and enter your servers URLs and API keys for each server.  
 2. Add the profile name (case insensitive) and movie path for the radarr instance the movies will be synced to:
    ```ini
    [radarrA]
    url = https://example.com:443
    key = XXXXX
    
    [radarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile = 1080p
    path = /data/4k_Movies
    ```
 3. Or if you want to sync two sonarr instances:
    ```ini
    [sonarrA]
    url = https://example.com:443
    key = XXXXX
    
    [sonarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile = 1080p
    path = /data/4k_Shows
 
 4. Or if you want to sync two lidarr instances:
    ```ini
    [lidarrA]
    url = https://example.com:443
    key = XXXXX
    
    [lidarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile = lossless
    path = /data/lossless_music

    **Note** you cannot have a mix of radarr, lidarr, or sonarr config setups at the same time.

 5. Optional Configuration
    ```ini
    [sonarrA]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile_filter = 1080p # add a filter to only sync contents belonging to this profile (can set by profile_filter_id as well)

    [sonarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile_id = 1 # Syncarr will try to find id from name but you can specify the id directly if you want
    language = Vietnamese # can set language for new content added (Sonarr v3 only) (can set by language_id as well)
    path = /data/4k_Movies

    [general]
    sync_bidirectionally = 1 # sync from instance A to B **AND** instance B to A
    auto_search = 0 # search is automatically started on new content - disable by setting to 0
    monitor_new_content = 0 # set to 0 to never monitor new content synced or to 1 to always monitor new content synced
    ```

    **Note** If `sync_bidirectionally` is set to `1`, then instance A will require either `profile_id` or `profile` AND `path` as well

---
## How to Run
 1. install the needed python modules (you'll need pip or you can install the modules manually inside the `requirements.txt` file):
    ```bash
    pip install -r requirements.txt
    ```
 2. run this script directly or through a Cron:
    ```bash
    python index.py
    ```

---
## Docker Compose
This script can run through a docker container with a set interval (default every 5 minutes)

```
syncarr:
    image: syncarr/syncarr:latest
    container_name: syncarr
    restart: unless-stopped
    environment:
        RADARR_A_URL: https://example.com:443
        RADARR_A_KEY: XXXXX
        RADARR_B_URL: http://127.0.0.1:8080
        RADARR_B_KEY: XXXXX
        RADARR_B_PROFILE: 1080p
        RADARR_B_PATH: /data/4k_Movies
        SYNC_INTERVAL_SECONDS: 300
```

or

```
syncarr:
    image: syncarr/syncarr:latest
    container_name: syncarr
    restart: unless-stopped
    environment:
        SONARR_A_URL: https://example.com:443
        SONARR_A_KEY: XXXXX
        SONARR_B_URL: http://127.0.0.1:8080
        SONARR_B_KEY: XXXXX
        SONARR_B_PROFILE: 1080p
        SONARR_B_PATH: /data/4k_Movies
        SYNC_INTERVAL_SECONDS: 300
```

or

```
syncarr:
    image: syncarr/syncarr:latest
    container_name: syncarr
    restart: unless-stopped
    environment:
        LIDARR_A_URL: https://example.com:443
        LIDARR_A_KEY: FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
        LIDARR_B_URL: http://127.0.0.1:8080
        LIDARR_B_KEY: FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
        LIDARR_B_PROFILE: 1080p
        LIDARR_B_PATH: /data/4k_Movies
        SYNC_INTERVAL_SECONDS: 300
```

---
## Docker
For just plain docker (radarr example):

```
docker run -it --rm --name syncarr -e RADARR_A_URL=https://example.com:443 -e RADARR_A_KEY=XXXXX -e RADARR_B_URL=http://127.0.0.1:8080 -e RADARR_B_KEY=XXXXX -e RADARR_B_PROFILE=1080p -e RADARR_B_PATH=/data/4k_Movies -e SYNC_INTERVAL_SECONDS=300 syncarr/syncarr
```

**Notes** 
* You can also specify the `PROFILE_ID` directly through the `*ARR_A_PROFILE_ID` and `*ARR_B_PROFILE_ID` ENV variables.
To filter by profile in docker use `ARR_A_PROFILE_FILTER` or `ARR_A_PROFILE_FILTER_ID` ENV variables. (same for `*arr_B` in bidirectional sync)
* Language for new content (Sonarr v3 only) can be set by `SONARR_B_LANGUAGE` or `SONARR_B_LANGUAGE_ID` (and `SONARR_B` if bidirectional sync)
* Set bidirectional sync with `SYNCARR_BIDIRECTIONAL_SYNC=1`
* Set disable auto searching on new content with `SYNCARR_AUTO_SEARCH=0`
* Set if you wanted to monitor new content with `SYNCARR_MONITOR_NEW_CONTENT=1/0`

---
## Requirements
 * Python 3.4 or greater
 * 2x Radarr/Sonarr/Lidarr servers
 * Install requirements.txt
 * 
---
## Troubleshooting
If you need to troubleshoot syncarr, then you can either set the log level through the config file:

```ini
[general]
log_level = 10
```
    
Or in docker, set the `LOG_LEVEL` ENV variable. Default is set to `20` (info only) but you can set to `10` to get debug info as well. When pasting debug logs online, **make sure to remove any apikeys and any other data you don't want others to see.**

---
## Disclaimer
Back up your instances before trying this out. I am not responsible for any lost data.

---

Enjoy my card? Help me out for a couple of :beers: or a :coffee:!

[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/JMISm06AD)
