#!/usr/bin/env python

import logging
import sys
import time


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

from syncarr.get_config import *


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
instanceA_profile = ''
instanceA_profile_id = ''
instanceA_profile_filter = ''
instanceA_path = ''

instanceB_url = ''
instanceB_key = ''
instanceB_profile = ''
instanceB_profile_id = ''
instanceB_profile_filter = ''
instanceB_path = ''

api_version = 'v1/' # we are going to detect what API version we are on
tested_api_version = False # only get api version once


api_content_path = '' # url path to add content
api_search_path = '' # url path to search for content on RSS feeds
api_profile_path = '' # url path to get quality profiles
api_status_path = '' # url path to check on server status

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
    instanceA_profile = sonarrA_profile
    instanceA_profile_id = sonarrA_profile_id
    instanceA_profile_filter = sonarrA_profile_filter
    instanceA_profile_filter_id = sonarrA_profile_filter_id
    instanceA_path = sonarrA_path

    instanceB_url = sonarrB_url
    instanceB_key = sonarrB_key
    instanceB_profile = sonarrB_profile
    instanceB_profile_id = sonarrB_profile_id
    instanceB_profile_filter = sonarrB_profile_filter
    instanceB_profile_filter_id = sonarrB_profile_filter_id
    instanceB_path = sonarrB_path

    api_version = ''
    api_content_path = 'series'
    api_search_path = 'command'
    api_profile_path = 'profile'
    api_status_path = 'system/status'

    content_id_key = 'tvdbId'
    is_sonarr = True

########################################################################################################################


logger.debug({
    'instanceA_url': instanceA_url,
    'instanceA_key': instanceA_key,
    'instanceB_path': instanceB_path,
    'instanceB_url': instanceB_url,
    'instanceB_key': instanceB_key,
    'instanceB_path': instanceB_path,
    'api_content_path': api_content_path,
    'api_search_path': api_search_path,
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

# if two way sync need instance A path and profile
if sync_bidirectionally:
    assert instanceA_path
    if not instanceB_profile_id and not instanceB_profile:
        logger.error('profile_id or profile is required for *arr instance A if sync bidirectionally is enabled')
        sys.exit(0)


if not instanceB_profile_id and not instanceB_profile:
    logger.error('profile_id or profile is required for *arr instance B')
    sys.exit(0)
