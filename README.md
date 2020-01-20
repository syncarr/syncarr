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
    key = FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
    
    [lidarrB]
    url = http://127.0.0.1:8080
    key = FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
    profile = lossless
    path = /data/lossless_music
    ```

 5. By default Syncarr will sync unidirectionally from instance A to instance B but you can add bidirectional syncing with:
     ```ini
     [general]
     sync_bidirectionally = 1
     ```
    If `sync_bidirectionally` is set to true, then instance A will require either `profile_id` or `profile` AND `path`

 6. syncarr will try to find the `profile_id` given a `profile` name, if no match is found, syncarr will exit with error. You can also specify a `profile_id` directly instead of a `profile` name:
     ```ini
    [radarrB]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile_id = 1
    path = /data/4k_Movies
    ```

 7. You can filter content to be synced only from a certain profile/profile_id by adding the `profile_filter` or `profile_filter_id` to instance A. The same goes to instance B if syncing bidirectionally.
    ```ini
     [radarrA]
    url = http://127.0.0.1:8080
    key = XXXXX
    profile_filter = 1080p
    ```
---

## Notes
* you cannot have a mix of radarr, lidarr, or sonarr config setups at the same time.
* for radarr, sonarr, and lidarr, an optional `profile` can be added to instance A so only content with that `profile` will be synced from instance A to instance B. This will be also true if bidirectional syncing is enabled **only** if both `profile`s are supplied. The same behavior can be spplied with `profile_id`s.


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

**Note:** 
You can also specify the `PROFILE_ID` directly through the `*ARR_A_PROFILE_ID` and `*ARR_B_PROFILE_ID` ENV variables.
To filter by profile in docker use `ARR_A_PROFILE_FILTER` or `ARR_A_PROFILE_FILTER_ID` ENV variables. (same for `*arr_B` in bidirectional sync)

---
## Requirements
 * Python 3.4 or greater
 * 2x Radarr/Sonarr/Lidarr servers
 * Install requirements.txt
 * 
---
## Debugging
If you need to debug syncarr then you can either set the log level through the config file:

```ini
[general]
log_level = 10
```
    
Or in docker, set the `LOG_LEVEL` ENV variable. Default is set to `20` (info only) but you can set to `10` to get debug info as well. When pasting debug logs online, **make sure to remove any apikeys and any other data you don't want others to see.**

---
## Disclaimer
Back up your instances before trying this out. I am not responsible for any lost data.
