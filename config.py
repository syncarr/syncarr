#!/usr/bin/env python

import logging
import os
import sys
import time

import configparser


DEV = os.environ.get('DEV')
VER = '1.5.0'

V3_API_PATH = 'v3/'

########################################################################################################################
# get docker based ENV vars
is_in_docker = os.environ.get('IS_IN_DOCKER')
instance_sync_interval_seconds = os.environ.get('SYNC_INTERVAL_SECONDS')
if instance_sync_interval_seconds:
    instance_sync_interval_seconds = int(instance_sync_interval_seconds)

########################################################################################################################

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
    if is_in_docker:
        return os.environ.get(env_key)

    try:
        _config = ConfigSectionMap(config_section)
        return _config.get(config_key)
    except configparser.NoSectionError:
        return ''

########################################################################################################################
# load config file


BASE_CONFIG = 'config.conf'
if DEV:
    settingsFilename = os.path.join(os.getcwd(), 'dev-{}'.format(BASE_CONFIG))
else:
    settingsFilename = os.path.join(os.getcwd(), BASE_CONFIG)

config = configparser.ConfigParser()
config.read(settingsFilename)

########################################################################################################################
# get config settings from ENV or config files for Radarr
radarrA_url = get_config_value('RADARR_A_URL', 'url', 'radarrA')
radarrA_key = get_config_value('RADARR_A_KEY', 'key', 'radarrA')
radarrA_profile = get_config_value('RADARR_A_PROFILE', 'profile', 'radarrA')
radarrA_profile_id = get_config_value(
    'RADARR_A_PROFILE_ID', 'profile_id', 'radarrA')
radarrA_profile_filter = get_config_value(
    'RADARR_A_PROFILE_FILTER', 'profile_filter', 'radarrA')
radarrA_profile_filter_id = get_config_value(
    'RADARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'radarrA')
radarrA_path = get_config_value('RADARR_A_PATH', 'path', 'radarrA')

radarrB_url = get_config_value('RADARR_B_URL', 'url', 'radarrB')
radarrB_key = get_config_value('RADARR_B_KEY', 'key', 'radarrB')
radarrB_profile = get_config_value('RADARR_B_PROFILE', 'profile', 'radarrB')
radarrB_profile_id = get_config_value(
    'RADARR_B_PROFILE_ID', 'profile_id', 'radarrB')
radarrB_profile_filter = get_config_value(
    'RADARR_B_PROFILE_FILTER', 'profile_filter', 'radarrB')
radarrB_profile_filter_id = get_config_value(
    'RADARR_B_PROFILE_FILTER_ID', 'profile_filter_id', 'radarrB')
radarrB_path = get_config_value('RADARR_B_PATH', 'path', 'radarrB')

# get config settings from ENV or config files for Sonarr
sonarrA_url = get_config_value('SONARR_A_URL', 'url', 'sonarrA')
sonarrA_key = get_config_value('SONARR_A_KEY', 'key', 'sonarrA')
sonarrA_path = get_config_value('SONARR_A_PATH', 'path', 'sonarrA')
sonarrA_profile = get_config_value('SONARR_A_PROFILE', 'profile', 'sonarrA')
sonarrA_profile_id = get_config_value(
    'SONARR_A_PROFILE_ID', 'profile_id', 'sonarrA')
sonarrA_profile_filter = get_config_value(
    'SONARR_A_PROFILE_FILTER', 'profile_filter', 'sonarrA')
sonarrA_profile_filter_id = get_config_value(
    'SONARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'sonarrA')
sonarrA_language = get_config_value('SONARR_A_LANGUAGE', 'language', 'sonarrA')
sonarrA_language_id = get_config_value('SONARR_A_LANGUAGE_ID', 'language_id', 'sonarrA')


sonarrB_url = get_config_value('SONARR_B_URL', 'url', 'sonarrB')
sonarrB_key = get_config_value('SONARR_B_KEY', 'key', 'sonarrB')
sonarrB_path = get_config_value('SONARR_B_PATH', 'path', 'sonarrB')
sonarrB_profile = get_config_value('SONARR_B_PROFILE', 'profile', 'sonarrB')
sonarrB_profile_id = get_config_value(
    'SONARR_B_PROFILE_ID', 'profile_id', 'sonarrB')
sonarrB_profile_filter = get_config_value(
    'SONARR_A_PROFILE_FILTER', 'profile_filter', 'sonarrB')
sonarrB_profile_filter_id = get_config_value(
    'SONARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'sonarrB')
sonarrB_language = get_config_value('SONARR_B_LANGUAGE', 'language', 'sonarrB')
sonarrB_language_id = get_config_value('SONARR_B_LANGUAGE_ID', 'language_id', 'sonarrB')

# get config settings from ENV or config files for Lidarr
lidarrA_url = get_config_value('LIDARR_A_URL', 'url', 'lidarrA')
lidarrA_key = get_config_value('LIDARR_A_KEY', 'key', 'lidarrA')
lidarrA_profile = get_config_value('LIDARR_A_PROFILE', 'profile', 'lidarrA')
lidarrA_profile_id = get_config_value(
    'LIDARR_A_PROFILE_ID', 'profile_id', 'lidarrA')
lidarrA_profile_filter = get_config_value(
    'LIDARR_A_PROFILE_FILTER', 'profile_filter', 'lidarrA')
lidarrA_profile_filter_id = get_config_value(
    'LIDARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'lidarrA')
lidarrA_path = get_config_value('LIDARR_A_PATH', 'path', 'lidarrA')

lidarrB_url = get_config_value('LIDARR_B_URL', 'url', 'lidarrB')
lidarrB_key = get_config_value('LIDARR_B_KEY', 'key', 'lidarrB')
lidarrB_profile = get_config_value('LIDARR_B_PROFILE', 'profile', 'lidarrB')
lidarrB_profile_id = get_config_value(
    'LIDARR_B_PROFILE_ID', 'profile_id', 'lidarrB')
lidarrB_profile_filter = get_config_value(
    'LIDARR_A_PROFILE_FILTER', 'profile_filter', 'lidarrB')
lidarrB_profile_filter_id = get_config_value(
    'LIDARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'lidarrB')
lidarrB_path = get_config_value('LIDARR_B_PATH', 'path', 'lidarrB')

# get general conf options
sync_bidirectionally = get_config_value(
    'SYNCARR_BIDIRECTIONAL_SYNC', 'bidirectional', 'general') or 0
if sync_bidirectionally:
    sync_bidirectionally = int(sync_bidirectionally) or 0
auto_search = get_config_value(
    'SYNCARR_AUTO_SEARCH', 'auto_search', 'general') or 0
if auto_search:
    auto_search = int(auto_search) or 0


########################################################################################################################
# setup logger

# CRITICAL 50, ERROR 40, WARNING 3, INFO 20, DEBUG 10, NOTSET 0
log_level = get_config_value('LOG_LEVEL', 'log_level', 'general') or 20
if log_level:
    log_level = int(log_level)

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
logger.info('log level {}'.format(log_level))

if DEV:
    logger.info('-----------------DEVV-----------------')
########################################################################################################################
# make sure we have radarr, lidarr, OR sonarr
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

########################################################################################################################
# get generic instanceA/B variables
instanceA_url = ''
instanceA_key = ''
instanceA_path = ''
instanceA_profile = ''
instanceA_profile_id = ''
instanceA_profile_filter = ''
instanceA_language_id = ''
instanceA_language = ''

instanceB_url = ''
instanceB_key = ''
instanceB_path = ''
instanceB_profile = ''
instanceB_profile_id = ''
instanceB_profile_filter = ''
instanceB_language_id = ''
instanceB_language = ''


api_version = 'v1/' # we are going to detect what API version we are on
tested_api_version = False # only get api version once


api_content_path = '' # url path to add content
api_search_path = '' # url path to search for content on RSS feeds
api_profile_path = '' # url path to get quality profiles
api_status_path = '' # url path to check on server status
api_language_path = '' # url to get lanaguge profiles

is_radarr = False
is_sonarr = False
is_lidarr = False

content_id_key = '' # the unique id for a content item

if radarrA_url and radarrB_url:
    instanceA_url = radarrA_url
    instanceA_key = radarrA_key
    instanceA_profile = radarrA_profile
    instanceA_profile_id = radarrA_profile_id
    instanceA_profile_filter = radarrA_profile_filter
    instanceA_profile_filter_id = radarrA_profile_filter_id
    instanceA_path = radarrA_path
    
    instanceB_url = radarrB_url
    instanceB_key = radarrB_key
    instanceB_profile = radarrB_profile
    instanceB_profile_id = radarrB_profile_id
    instanceB_profile_filter = radarrB_profile_filter
    instanceB_profile_filter_id = radarrB_profile_filter_id
    instanceB_path = radarrB_path

    api_version = '' # radarr v2 doesnt have version in api url
    api_content_path = 'movie'
    api_search_path = 'command'
    api_profile_path = 'profile'
    api_status_path = 'system/status'

    content_id_key = 'tmdbId'
    is_radarr = True

elif lidarrA_url and lidarrB_url:
    instanceA_url = lidarrA_url
    instanceA_key = lidarrA_key
    instanceA_profile = lidarrA_profile
    instanceA_profile_id = lidarrA_profile_id
    instanceA_profile_filter = lidarrA_profile_filter
    instanceA_profile_filter_id = lidarrA_profile_filter_id
    instanceA_path = lidarrA_path

    instanceB_url = lidarrB_url
    instanceB_key = lidarrB_key
    instanceB_profile = lidarrB_profile
    instanceB_profile_id = lidarrB_profile_id
    instanceB_profile_filter = lidarrB_profile_filter
    instanceB_profile_filter_id = lidarrB_profile_filter_id
    instanceB_path = lidarrB_path

    api_version = 'v1/'
    api_content_path = 'artist'
    api_search_path = 'command'
    api_profile_path = 'qualityprofile'
    api_status_path = 'system/status'

    content_id_key = 'foreignArtistId'
    is_lidarr = True

elif sonarrA_url and sonarrB_url:
    instanceA_url = sonarrA_url
    instanceA_key = sonarrA_key
    instanceA_path = sonarrA_path
    instanceA_profile = sonarrA_profile
    instanceA_profile_id = sonarrA_profile_id
    instanceA_profile_filter = sonarrA_profile_filter
    instanceA_profile_filter_id = sonarrA_profile_filter_id
    instanceA_language = sonarrA_language
    instanceA_language_id = sonarrA_language_id

    instanceB_url = sonarrB_url
    instanceB_key = sonarrB_key
    instanceB_path = sonarrB_path
    instanceB_profile = sonarrB_profile
    instanceB_profile_id = sonarrB_profile_id
    instanceB_profile_filter = sonarrB_profile_filter
    instanceB_profile_filter_id = sonarrB_profile_filter_id
    instanceB_language = sonarrB_language
    instanceB_language_id = sonarrB_language_id


    api_version = ''
    api_content_path = 'series'
    api_search_path = 'command'
    api_profile_path = 'profile'
    api_status_path = 'system/status'
    api_language_path = 'languageprofile'

    content_id_key = 'tvdbId'
    is_sonarr = True

########################################################################################################################
# path generators

def get_path(instance_url, api_path, key, checkV3=False):
    global api_version, api_profile_path

    if not tested_api_version:
        logger.debug(f'checkV3: "{checkV3}" for {instance_url}')

    if checkV3:
        api_version = V3_API_PATH

    if checkV3 and is_sonarr:
        api_profile_path = 'qualityprofile'

    url = f"{instance_url}/api/{api_version}{api_path}?apikey={key}"
    return url

def get_status_path(instance_url, key, checkV3):
    url = get_path(instance_url, api_status_path, key, checkV3)
    logger.debug('get_status_path: {}'.format(url))
    return url

def get_content_path(instance_url, key):
    url = get_path(instance_url, api_content_path, key)
    logger.debug('get_content_path: {}'.format(url))
    return url

def get_search_path(instance_url, key):
    url = get_path(instance_url, api_search_path, key)
    logger.debug('get_search_path: {}'.format(url))
    return url

def get_language_path(instance_url, key):
    print('-'*20)
    print(instance_url)
    print('-'*20)
    url = get_path(instance_url, api_language_path, key)
    logger.debug('get_language_path: {}'.format(url))
    return url

def get_profile_path(instance_url, key):
    url = get_path(instance_url, api_profile_path, key)
    logger.debug('get_profile_path: {}'.format(url))
    return url

########################################################################################################################
# check for required fields

logger.debug({
    'instanceA_url': instanceA_url,
    'instanceA_key': instanceA_key,
    'instanceA_path': instanceA_path,
    'instanceB_url': instanceB_url,
    'instanceB_key': instanceB_key,
    'instanceB_path': instanceB_path,
    'api_content_path': api_content_path,
    'api_search_path': api_search_path,
    'api_language_path': api_language_path,
    'is_sonarr': is_sonarr,
    'is_lidarr': is_lidarr,
})

if not instanceA_url:
    logger.error('missing URL for instance A')
    sys.exit(0)

if not instanceA_key:
    logger.error('missing API key for instance A')
    sys.exit(0)

if not instanceA_url:
    logger.error('missing URL for instance B')
    sys.exit(0)

if not instanceB_key:
    logger.error('missing API key for instance B')
    sys.exit(0)

if not api_content_path:
    logger.error('missing api_content_path')
    sys.exit(0)

if not api_search_path:
    logger.error('missing api_search_path')
    sys.exit(0)

if not content_id_key:
    logger.error('missing content_id_key')
    sys.exit(0)

# if two way sync need instance A path and profile
if sync_bidirectionally:
    assert instanceA_path
    if not instanceB_profile_id and not instanceB_profile:
        logger.error('profile_id or profile is required for *arr instance A if sync bidirectionally is enabled')
        sys.exit(0)


if not instanceB_profile_id and not instanceB_profile:
    logger.error('profile_id or profile is required for *arr instance B')
    sys.exit(0)
