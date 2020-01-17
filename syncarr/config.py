#!/usr/bin/env python

import os
import logging
import requests
import json
import configparser
import sys
import time

DEV = os.environ.get('DEV', False)


VER = '1.2.0'

def ConfigSectionMap(section):
    '''get all config options from config file'''
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def get_config_value(env_key, config_key, config_section):
    value = ''
    _config = {}
    try:
        _config = ConfigSectionMap(config_section)
    except configparser.NoSectionError:
        return ''

    if is_in_docker:
        value = os.environ.get(env_key)
    else:
        value = _config.get(config_key)

    return value

########################################################################################################################

# load config file
BASE_CONFIG = 'config.conf'
if DEV:
    settingsFilename = os.path.join(os.getcwd(), 'dev-{}'.format(BASE_CONFIG))
else:
    settingsFilename = os.path.join(os.getcwd(), BASE_CONFIG)

config = configparser.ConfigParser()
config.read(settingsFilename)

is_in_docker = os.environ.get('IS_IN_DOCKER')
radarr_sync_interval_seconds = os.environ.get('SYNC_INTERVAL_SECONDS')
if radarr_sync_interval_seconds:
    radarr_sync_interval_seconds = int(radarr_sync_interval_seconds)

########################################################################################################################
# setup logger

# CRITICAL 50, ERROR 40, WARNING 3, INFO 20, DEBUG 10, NOTSET 0
log_level = get_config_value('LOG_LEVEL', 'log_level', 'general') or 20
if log_level:
    log_level = int(log_level)

print('log_level', log_level)

logger = logging.getLogger()
logger.setLevel(log_level)

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

# log to txt file
fileHandler = logging.FileHandler("./output.txt")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# log to std out
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

logger.debug('Syncarr Version {}'.format(VER))
########################################################################################################################


########################################################################################################################
# get config settings from ENV or config files for Radarr
radarrA_url = get_config_value('RADARR_A_URL', 'url', 'radarrA')
radarrA_key = get_config_value('RADARR_A_KEY', 'key', 'radarrA')
radarrA_profile = get_config_value('RADARR_A_PROFILE', 'profile', 'radarrA')
radarrA_profile_id = get_config_value('RADARR_A_PROFILE_ID', 'profile_id', 'radarrA')
radarrA_path = get_config_value('RADARR_A_PATH', 'path', 'radarrA')
radarrA_is_version_3 = get_config_value('RADARR_A_VERSION_3', 'version3', 'radarrA')
radarrB_url = get_config_value('RADARR_B_URL', 'url', 'radarrB')
radarrB_key = get_config_value('RADARR_B_KEY', 'key', 'radarrB')
radarrB_profile = get_config_value('RADARR_B_PROFILE', 'profile', 'radarrB')
radarrB_profile_id = get_config_value('RADARR_B_PROFILE_ID', 'profile_id', 'radarrB')
radarrB_path = get_config_value('RADARR_B_PATH', 'path', 'radarrB')
radarrB_is_version_3 = get_config_value('RADARR_B_VERSION_3', 'version3', 'radarrB')

# get config settings from ENV or config files for Sonarr
sonarrA_url = get_config_value('SONARR_A_URL', 'url', 'sonarrA')
sonarrA_key = get_config_value('SONARR_A_KEY', 'key', 'sonarrA')
sonarrA_profile = get_config_value('SONARR_A_PROFILE', 'profile', 'sonarrA')
sonarrA_profile_id = get_config_value('SONARR_A_PROFILE_ID', 'profile_id', 'sonarrA')
sonarrA_path = get_config_value('SONARR_A_PATH', 'path', 'sonarrA')
sonarrB_url = get_config_value('SONARR_B_URL', 'url', 'sonarrB')
sonarrB_key = get_config_value('SONARR_B_KEY', 'key', 'sonarrB')
sonarrB_profile = get_config_value('SONARR_B_PROFILE', 'profile', 'sonarrB')
sonarrB_profile_id = get_config_value('SONARR_B_PROFILE_ID', 'profile_id', 'sonarrB')
sonarrB_path = get_config_value('SONARR_B_PATH', 'path', 'sonarrB')

# get config settings from ENV or config files for Lidarr
lidarrA_url = get_config_value('LIDARR_A_URL', 'url', 'lidarrA')
lidarrA_key = get_config_value('LIDARR_A_KEY', 'key', 'lidarrA')
lidarrA_profile = get_config_value('LIDARR_A_PROFILE', 'profile', 'lidarrA')
lidarrA_profile_id = get_config_value('LIDARR_A_PROFILE_ID', 'profile_id', 'lidarrA')
lidarrA_path = get_config_value('LIDARR_A_PATH', 'path', 'lidarrA')
lidarrB_url = get_config_value('LIDARR_B_URL', 'url', 'lidarrB')
lidarrB_key = get_config_value('LIDARR_B_KEY', 'key', 'lidarrB')
lidarrB_profile = get_config_value('LIDARR_B_PROFILE', 'profile', 'lidarrB')
lidarrB_profile_id = get_config_value('LIDARR_B_PROFILE_ID', 'profile_id', 'lidarrB')
lidarrB_path = get_config_value('LIDARR_B_PATH', 'path', 'lidarrB')

# get general conf options
sync_bidirectionally = get_config_value('SYNCARR_BIDIRECTIONAL_SYNC', 'bidirectional', 'general') or 0
if sync_bidirectionally:
    sync_bidirectionally = int(sync_bidirectionally) or 0

########################################################################################################################
# find if we are syncing radarr, lidarr, or sonarr
instanceA_url = ''
instanceA_key = ''
instanceB_url = ''
instanceB_key = ''
instanceB_profile_id = ''
instanceB_path = ''
api_content_path = ''
api_search_path = ''

is_radarr = False
is_sonarr = False
is_lidarr = False
instanceA_is_v3 = False
instanceB_is_v3 = False


if radarrA_url and radarrB_url:
    assert radarrA_url
    assert radarrA_key
    assert radarrB_url
    assert radarrB_key
    assert radarrB_profile_id
    assert radarrB_path

    instanceA_url = radarrA_url
    instanceA_key = radarrA_key
    instanceB_url = radarrB_url
    instanceB_key = radarrB_key
    instanceB_profile_id = radarrB_profile_id
    instanceB_path = radarrB_path

    api_content_path = 'api/movie'
    api_search_path = 'api/command'
    content_id_key = 'tmdbId'

    is_radarr = True
    instanceA_is_v3 = False if radarrA_is_version_3 else True
    instanceB_is_v3 = False if radarrB_is_version_3 else True

elif lidarrA_url and lidarrB_url:
    assert lidarrA_url
    assert lidarrA_key
    assert lidarrB_url
    assert lidarrB_key
    assert lidarrB_profile_id
    assert lidarrB_path

    instanceA_url = lidarrA_url
    instanceA_key = lidarrA_key
    instanceB_url = lidarrB_url
    instanceB_key = lidarrB_key
    instanceB_profile_id = lidarrB_profile_id
    instanceB_path = lidarrB_path

    api_content_path = 'api/v1/artist'
    api_search_path = 'api/v1/command'
    content_id_key = 'foreignArtistId'

    is_lidarr = True
    instanceA_is_v3 = True
    instanceB_is_v3 = True

elif sonarrA_url and sonarrB_url:
    assert sonarrA_url
    assert sonarrA_key
    assert sonarrB_url
    assert sonarrB_key
    assert sonarrB_profile_id
    assert sonarrB_path

    instanceA_url = sonarrA_url
    instanceA_key = sonarrA_key
    instanceB_url = sonarrB_url
    instanceB_key = sonarrB_key
    instanceB_profile_id = sonarrB_profile_id
    instanceB_path = sonarrB_path

    api_content_path = 'api/v3/series'
    api_search_path = 'api/command'
    content_id_key = 'tvdbId'

    is_sonarr = True
    instanceA_is_v3 = True
    instanceB_is_v3 = True

########################################################################################################################

logger.debug({
    'instanceA_url': instanceA_url,
    'instanceA_key': instanceA_key,
    'instanceB_url': instanceB_url,
    'instanceB_key': instanceB_key,
    'instanceB_profile_id': instanceB_profile_id,
    'instanceB_path': instanceB_path,
    'api_content_path': api_content_path,
    'api_search_path': api_search_path,
    'instanceA_is_v3': instanceA_is_v3,
    'instanceB_is_v3': instanceB_is_v3,
    'is_sonarr': is_sonarr,
    'is_lidarr': is_lidarr,
})

assert instanceA_url
assert instanceA_key
assert instanceB_url
assert instanceB_key

assert api_content_path
assert api_search_path
assert content_id_key

########################################################################################################################
# make sure we have radarr OR sonarr
if (
    (sonarrA_url and radarrA_url) or 
    (sonarrA_url and radarrB_url) or
    (sonarrA_url and lidarrA_url) or
    (sonarrA_url and lidarrB_url) or

    (radarrA_url and lidarrA_url) or
    (radarrA_url and lidarrB_url) or
    (radarrB_url and lidarrA_url) or
    (radarrB_url and lidarrB_url)
):
    logger.error('cannot have more than one *arr type profile(s) setup at the same time')
    sys.exit(0)
