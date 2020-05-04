# Syncarr
Syncs two Radarr/Sonarr/Lidarr servers through the web API. Useful for syncing a 4k Radarr/Sonarr instance to a 1080p Radarr/Sonarr instance.

* Supports Radarr/Sonarr version 2 and 3.
* Can sync by `profile` name or `profile_id`
* Filter what media gets synced by `profile` name or `profile_id`
* Supports Docker for multiple instances
* Can set interval for syncing
* Support two way sync (one way by default)
* Set language profiles (Sonarr v3 only)
* Filter syncing by content file quality (Radarr only)
* Filter syncing by tags (Sonarr only)


## Configuration
 1. Edit the config.conf file and enter your servers URLs and API keys for each server.  
 2. Add the profile name (case insensitive) and movie path for the Radarr instance the movies will be synced to:
    ```ini
    [radarrA]
    url = https://4k.example.com:443
    key = XXXXX
    
    [radarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile = 1080p
    path = /data/Movies
    ```
 3. Or if you want to sync two Sonarr instances:
    ```ini
    [sonarrA]
    url = https://4k.example.com:443
    key = XXXXX
    
    [sonarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile = 1080p
    path = /data/Shows
 
 4. Or if you want to sync two Lidarr instances:
    ```ini
    [lidarrA]
    url = https://lossless.example.com:443
    key = XXXXX
    
    [lidarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile = Standard
    path = /data/Music
    ```
    
    **Note** you cannot have a mix of Radarr, Lidarr, or Sonarr config setups at the same time.

 5. Optional Configuration
    ```ini
    [*arrA]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile_filter = 1080p # add a filter to only sync contents belonging to this profile (can set by profile_filter_id as well)
    quality_match = HD- # (Radarr only) regex match to only sync content that matches the set quality (ie if set to 1080p then only movies with matching downloaded quality of 1080p will be synced)
    tag_filter = Horror # (Sonarr only) sync movies by tag name (seperate multiple tags by comma (no spaces) ie horror,comedy,action)
    tag_filter_id = 2 # (Sonarr only) sync movies by tag id (seperate multiple tags by comma (no spaces) ie 2,3,4)

    [*arrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile_id = 1 # Syncarr will try to find id from name but you can specify the id directly if you want
    language = Vietnamese # can set language for new content added (Sonarr v3 only) (can set by language_id as well)
    path = /data/Movies

    [general]
    sync_bidirectionally = 1 # sync from instance A to B **AND** instance B to A
    auto_search = 0 # search is automatically started on new content - disable by setting to 0
    monitor_new_content = 0 # set to 0 to never monitor new content synced or to 1 to always monitor new content synced
    ```

    **Note** If `sync_bidirectionally` is set to `1`, then instance A will require either `profile_id` or `profile` AND `path` as well

---

## Requirements
 * Python 3.6 or greater
 * 2 Radarr, Sonarr, or Lidarr servers
  
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
        RADARR_A_URL: https://4k.example.com:443
        RADARR_A_KEY: XXXXX
        RADARR_B_URL: http://127.0.0.1:8080
        RADARR_B_KEY: XXXXX
        RADARR_B_PROFILE: 1080p
        RADARR_B_PATH: /data/Movies
        SYNC_INTERVAL_SECONDS: 300
```

or

```
syncarr:
    image: syncarr/syncarr:latest
    container_name: syncarr
    restart: unless-stopped
    environment:
        SONARR_A_URL: https://4k.example.com:443
        SONARR_A_KEY: XXXXX
        SONARR_B_URL: http://127.0.0.1:8080
        SONARR_B_KEY: XXXXX
        SONARR_B_PROFILE: 1080p
        SONARR_B_PATH: /data/Shows
        SYNC_INTERVAL_SECONDS: 300
```

or

```
syncarr:
    image: syncarr/syncarr:latest
    container_name: syncarr
    restart: unless-stopped
    environment:
        LIDARR_A_URL: https://lossless.example.com:443
        LIDARR_A_KEY: XXXXX
        LIDARR_B_URL: http://127.0.0.1:8080
        LIDARR_B_KEY: XXXXX
        LIDARR_B_PROFILE: Standard
        LIDARR_B_PATH: /data/Music
        SYNC_INTERVAL_SECONDS: 300
```

---
## Docker
For just plain docker (radarr example):

```
docker run -it --rm --name syncarr -e RADARR_A_URL=https://4k.example.com:443 -e RADARR_A_KEY=XXXXX -e RADARR_B_URL=http://127.0.0.1:8080 -e RADARR_B_KEY=XXXXX -e RADARR_B_PROFILE=1080p -e RADARR_B_PATH=/data/Movies -e SYNC_INTERVAL_SECONDS=300 syncarr/syncarr
```

**Notes** 
* You can also specify the `PROFILE_ID` directly through the `*ARR_A_PROFILE_ID` and `*ARR_B_PROFILE_ID` ENV variables.
To filter by profile in docker use `ARR_A_PROFILE_FILTER` or `ARR_A_PROFILE_FILTER_ID` ENV variables. (same for `*arr_B` in bidirectional sync)
* Language for new content (Sonarr v3 only) can be set by `SONARR_B_LANGUAGE` or `SONARR_B_LANGUAGE_ID` (and `SONARR_B` if bidirectional sync)
* Set bidirectional sync with `SYNCARR_BIDIRECTIONAL_SYNC=1` (default 0)
* Set disable auto searching on new content with `SYNCARR_AUTO_SEARCH=0`  (default 1)
* Set if you want to NOT monitor new content with `SYNCARR_MONITOR_NEW_CONTENT=0`  (default 1)
* Match regex quality profiles with `*ARR_A_QUALITY_MATCH` or `*ARR_B_QUALITY_MATCH`
* Filter by tag names or ids with `*ARR_A_TAG_FILTER` / `*ARR_B_TAG_FILTER` or `*ARR_A_TAG_FILTER_ID` / `*ARR_B_TAG_FILTER_ID`
  
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
