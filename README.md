# Syncarr
Syncs two Radarr servers from radarrA to radarrB (unidirectional) through the web API.  

### Configuration
 1. Edit the Config.txt file and enter your servers URLs and API keys for each server.  
 2. Add the profile id and movie path for the radarr instance the movies will be synced to

    Example Config.txt:
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

#### Requirements
 * Python 3.4 or greater
 * 2x Radarr servers
 * Install requirements.txt
