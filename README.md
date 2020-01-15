# Syncarr
Syncs two Radarr/Sonarr servers through the web API.

### Configuration
 1. Edit the config.conf file and enter your servers URLs and API keys for each server.  
 2. Add the profile id and movie path for the radarr instance the movies will be synced to
    ```ini
    [radarrA]
    url = https://example.com:443
    key = FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
    
    [radarrB]
    url = http://127.0.0.1:8080
    key = FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
    profile_id = 1
    path = /data/4k_Movies
    ```
 3. Or if you want to sync two sonarr instances:
    ```ini
    [sonarrA]
    url = https://example.com:443
    key = FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
    
    [sonarrB]
    url = http://127.0.0.1:8080
    key = FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
    profile_id = 1
    path = /data/4k_Movies
    ```

    **Note**: you cannot have both radarr and sonarr config setup at the same time.

 4. By default Syncarr will sync unidirectionally from instance A to instance B but you can add bidirectional syncing with:
     ```ini
     [general]
     sync_bidirectionally = 1
     ```

#### How to Run
You can run this script directly or through a Cron:
```bash
python index.py
```

#### Docker Compose
This script can be ran through a docker container with a set interval (default every 5 minutes)

```
syncarr:
    image: syncarr/syncarr:latest
    container_name: syncarr
    restart: unless-stopped
    environment:
        RADARR_A_URL: https://example.com:443
        RADARR_A_KEY: FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
        RADARR_B_URL: http://127.0.0.1:8080
        RADARR_B_KEY: FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
        RADARR_B_PROFILE_ID: 1
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
        SONARR_A_KEY: FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
        SONARR_B_URL: http://127.0.0.1:8080
        SONARR_B_KEY: FCKGW-RHQQ2-YXRKT-8TG6W-2B7Q8
        SONARR_B_PROFILE_ID: 1
        SONARR_B_PATH: /data/4k_Movies
        SYNC_INTERVAL_SECONDS: 300
```

#### Requirements
 * Python 3.4 or greater
 * 2x Radarr/Sonarr servers
 * Install requirements.txt



#### Disclaimer
Back up your instances before trying this out. I am not responsible for any lost data.
