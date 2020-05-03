#!/usr/bin/env python

import logging
import os
import sys
import time

import configparser


DEV = os.environ.get('DEV')
VER = '1.7.7'
DEBUG_LINE = '-' * 20

V1_API_PATH = 'v1/'
V2_API_PATH = ''
V3_API_PATH = 'v3/'

# https://github.com/lidarr/Lidarr/wiki/Artist
# https://github.com/Radarr/Radarr/wiki/API:Movie
# https://github.com/Sonarr/Sonarr/wiki/Series

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
        value = os.environ.get(env_key)
        if value is not None:  # only return if given value else try config file
            return value

    try:
        _config = ConfigSectionMap(config_section)
        return _config.get(config_key)
    except configparser.NoSectionError:
        return None

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
radarrA_profile_id = get_config_value('RADARR_A_PROFILE_ID', 'profile_id', 'radarrA')
radarrA_profile_filter = get_config_value('RADARR_A_PROFILE_FILTER', 'profile_filter', 'radarrA')
radarrA_quality_match = get_config_value('SONARR_A_QUALITY_MATCH', 'quality_match', 'sonarrA')
radarrA_profile_filter_id = get_config_value('RADARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'radarrA')
radarrA_path = get_config_value('RADARR_A_PATH', 'path', 'radarrA')

radarrB_url = get_config_value('RADARR_B_URL', 'url', 'radarrB')
radarrB_key = get_config_value('RADARR_B_KEY', 'key', 'radarrB')
radarrB_profile = get_config_value('RADARR_B_PROFILE', 'profile', 'radarrB')
radarrB_profile_id = get_config_value('RADARR_B_PROFILE_ID', 'profile_id', 'radarrB')
radarrB_profile_filter = get_config_value('RADARR_B_PROFILE_FILTER', 'profile_filter', 'radarrB')
radarrB_profile_filter_id = get_config_value('RADARR_B_PROFILE_FILTER_ID', 'profile_filter_id', 'radarrB')
radarrB_quality_match = get_config_value('RADARR_B_QUALITY_MATCH', 'quality_match', 'radarrB')
radarrB_path = get_config_value('RADARR_B_PATH', 'path', 'radarrB')

# get config settings from ENV or config files for Sonarr
sonarrA_url = get_config_value('SONARR_A_URL', 'url', 'sonarrA')
sonarrA_key = get_config_value('SONARR_A_KEY', 'key', 'sonarrA')
sonarrA_path = get_config_value('SONARR_A_PATH', 'path', 'sonarrA')
sonarrA_profile = get_config_value('SONARR_A_PROFILE', 'profile', 'sonarrA')
sonarrA_profile_id = get_config_value('SONARR_A_PROFILE_ID', 'profile_id', 'sonarrA')
sonarrA_profile_filter = get_config_value('SONARR_A_PROFILE_FILTER', 'profile_filter', 'sonarrA')
sonarrA_profile_filter_id = get_config_value('SONARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'sonarrA')
sonarrA_quality_match = get_config_value('SONARR_A_QUALITY_MATCH', 'quality_match', 'sonarrA')
sonarrA_language = get_config_value('SONARR_A_LANGUAGE', 'language', 'sonarrA')
sonarrA_language_id = get_config_value('SONARR_A_LANGUAGE_ID', 'language_id', 'sonarrA')


sonarrB_url = get_config_value('SONARR_B_URL', 'url', 'sonarrB')
sonarrB_key = get_config_value('SONARR_B_KEY', 'key', 'sonarrB')
sonarrB_path = get_config_value('SONARR_B_PATH', 'path', 'sonarrB')
sonarrB_profile = get_config_value('SONARR_B_PROFILE', 'profile', 'sonarrB')
sonarrB_profile_id = get_config_value('SONARR_B_PROFILE_ID', 'profile_id', 'sonarrB')
sonarrB_profile_filter = get_config_value('SONARR_B_PROFILE_FILTER', 'profile_filter', 'sonarrB')
sonarrB_profile_filter_id = get_config_value('SONARR_B_PROFILE_FILTER_ID', 'profile_filter_id', 'sonarrB')
sonarrB_quality_match = get_config_value('SONARR_B_QUALITY_MATCH', 'quality_match', 'sonarrB')
sonarrB_language = get_config_value('SONARR_B_LANGUAGE', 'language', 'sonarrB')
sonarrB_language_id = get_config_value('SONARR_B_LANGUAGE_ID', 'language_id', 'sonarrB')

# get config settings from ENV or config files for Lidarr
lidarrA_url = get_config_value('LIDARR_A_URL', 'url', 'lidarrA')
lidarrA_key = get_config_value('LIDARR_A_KEY', 'key', 'lidarrA')
lidarrA_profile = get_config_value('LIDARR_A_PROFILE', 'profile', 'lidarrA')
lidarrA_profile_id = get_config_value('LIDARR_A_PROFILE_ID', 'profile_id', 'lidarrA')
lidarrA_profile_filter = get_config_value('LIDARR_A_PROFILE_FILTER', 'profile_filter', 'lidarrA')
lidarrA_profile_filter_id = get_config_value('LIDARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'lidarrA')
lidarrA_quality_match = get_config_value('LIDARR_A_QUALITY_MATCH', 'quality_match', 'lidarrA')
lidarrA_path = get_config_value('LIDARR_A_PATH', 'path', 'lidarrA')

lidarrB_url = get_config_value('LIDARR_B_URL', 'url', 'lidarrB')
lidarrB_key = get_config_value('LIDARR_B_KEY', 'key', 'lidarrB')
lidarrB_profile = get_config_value('LIDARR_B_PROFILE', 'profile', 'lidarrB')
lidarrB_profile_id = get_config_value('LIDARR_B_PROFILE_ID', 'profile_id', 'lidarrB')
lidarrB_profile_filter = get_config_value('LIDARR_B_PROFILE_FILTER', 'profile_filter', 'lidarrB')
lidarrB_profile_filter_id = get_config_value('LIDARR_B_PROFILE_FILTER_ID', 'profile_filter_id', 'lidarrB')
lidarrB_quality_match = get_config_value('LIDARR_B_QUALITY_MATCH', 'quality_match', 'lidarrB')
lidarrB_path = get_config_value('LIDARR_B_PATH', 'path', 'lidarrB')


# set to search if config not set
sync_bidirectionally = get_config_value('SYNCARR_BIDIRECTIONAL_SYNC', 'bidirectional', 'general')
if sync_bidirectionally is not None:
    try:
        sync_bidirectionally = int(sync_bidirectionally)
    except ValueError:
        sync_bidirectionally = 0
else:
    sync_bidirectionally = 0

# set to search if config not set
auto_search = get_config_value('SYNCARR_AUTO_SEARCH', 'auto_search', 'general')
if auto_search is not None:
    try:
        auto_search = int(auto_search)
    except ValueError:
        auto_search = 0
else:
    auto_search = 1

# set to monitor if config not set
monitor_new_content = get_config_value('SYNCARR_MONITOR_NEW_CONTENT', 'monitor_new_content', 'general')
if monitor_new_content is not None:
    monitor_new_content = int(monitor_new_content)
else:
    monitor_new_content = 1

########################################################################################################################
# setup logger

# CRITICAL 50, ERROR 40, WARNING 3, INFO 20, DEBUG 10, NOTSET 0
log_level = get_config_value('LOG_LEVEL', 'log_level', 'general') or 20
if log_level:
    try:
        log_level = int(log_level)
    except ValueError:
        log_level = 20

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
instanceA_quality_match = ''

instanceB_url = ''
instanceB_key = ''
instanceB_path = ''
instanceB_profile = ''
instanceB_profile_id = ''
instanceB_profile_filter = ''
instanceB_language_id = ''
instanceB_language = ''
instanceB_quality_match = ''


api_version = ''  # we are going to detect what API version we are on
tested_api_version = False  # only get api version once


api_content_path = ''  # url path to add content
api_profile_path = ''  # url path to get quality profiles
api_status_path = ''  # url path to check on server status
api_language_path = ''  # url to get lanaguge profiles

is_radarr = False
is_sonarr = False
is_lidarr = False

content_id_key = ''  # the unique id for a content item

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

    api_version = V2_API_PATH  # radarr v2 doesnt have version in api url
    api_content_path = 'movie'
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

    api_version = V1_API_PATH
    api_content_path = 'artist'
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

    api_version = V3_API_PATH  # for sonarr try v3 first
    api_content_path = 'series'
    api_profile_path = 'qualityprofile'
    api_status_path = 'system/status'
    api_language_path = 'languageprofile'

    content_id_key = 'tvdbId'
    is_sonarr = True

########################################################################################################################
# path generators


def get_path(instance_url, api_path, key, changed_api_version=False):
    global api_version, api_profile_path

    if changed_api_version:
        api_version = V3_API_PATH

    # for sonarr - we check v3 first then v2
    if is_sonarr and changed_api_version:
        api_version = V2_API_PATH
        api_profile_path = 'profile'

    logger.debug(DEBUG_LINE)
    logger.debug({
        'instance_url': instance_url,
        'api_path': api_path,
        'api_version': api_version,
        'is_sonarr': is_sonarr,
        'api_profile_path': api_profile_path,
        'changed_api_version': changed_api_version,
    })

    url = f"{instance_url}/api/{api_version}{api_path}?apikey={key}"
    return url


def get_status_path(instance_url, key, changed_api_version):
    url = get_path(instance_url, api_status_path, key, changed_api_version)
    logger.debug('get_status_path: {}'.format(url))
    return url


def get_content_path(instance_url, key):
    url = get_path(instance_url, api_content_path, key)
    logger.debug('get_content_path: {}'.format(url))
    return url


def get_language_path(instance_url, key):
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
    'api_profile_path': api_profile_path,
    'api_language_path': api_language_path,
    'is_sonarr': is_sonarr,
    'is_lidarr': is_lidarr,
    'monitor_new_content': monitor_new_content,
    'sync_bidirectionally': sync_bidirectionally,
    'auto_search': auto_search,
    'api_version': api_version,
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
