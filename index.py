#!/usr/bin/env python

import os
import logging
import requests
import json
import configparser
import sys
import time

DEV = False
VER = '1.0.1'

# load config file
if DEV:
    settingsFilename = os.path.join(os.getcwd(), 'dev-Config.txt')
else:
    settingsFilename = os.path.join(os.getcwd(), 'Config.txt')

Config = configparser.ConfigParser()
Config.read(settingsFilename)

is_in_docker = os.environ.get('IS_IN_DOCKER')
radarr_sync_interval_seconds = os.environ.get('SYNC_INTERVAL_SECONDS')
if radarr_sync_interval_seconds:
    radarr_sync_interval_seconds = int(radarr_sync_interval_seconds)

########################################################################################################################
# setup logger
logger = logging.getLogger()
if DEV:
    logger.setLevel(logging.DEBUG)
else: 
    logger.setLevel(logging.INFO)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

# log to txt file
fileHandler = logging.FileHandler("./Output.txt")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# log to std out
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

logger.debug('RadarSync Version {}'.format(VER))
########################################################################################################################

def ConfigSectionMap(section):
    '''get all config options from config file'''
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                logger.debug("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def get_config_value(env_key, config_key, config_section):
    value = ''
    config = ConfigSectionMap(config_section)

    if is_in_docker:
        value = os.environ.get(env_key)
    else:
        value = config.get(config_key)

    return value


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

# find if we are syncing radarr or sonarr
instanceA_url = ''
instanceA_key = ''
instanceB_url = ''
instanceB_key = ''
instanceB_profile_id = ''
instanceB_path = ''
api_content_path = ''
api_search_path = ''

instanceA_is_v3 = False
instanceB_is_v3 = False
is_sonarr = False

if radarrA_url or radarrB_url:
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

    instanceA_is_v3 = False if radarrA_is_version_3 == 1 else True
    instanceB_is_v3 = False if radarrB_is_version_3 == 1 else True

else:
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

    # sonarr is v3 by default
    instanceA_is_v3 = True
    instanceB_is_v3 = True

# make sure we have radarr OR sonarr
if (sonarrA_url and radarrA_url) or (sonarrA_url and radarrB_url):
    logger.error('cannot have sonarr AND radarr profile(s) setup at the same time')
    sys.exit(0)


def get_new_content_payload(content, images):
    if is_sonarr:
        return {
            'title': content['title'],
            'qualityProfileId': content['qualityProfileId'],
            'titleSlug': content['titleSlug'],
            content_id_key: content[content_id_key],
            'year': content['year'],
            'monitored': content['monitored'],
            'minimumAvailability': 'released',
            'rootFolderPath': instanceB_path,
            'images': images,
            'profileId': instanceB_profile_id,
        }
    else :
        return {
            'title': content['title'],
            'qualityProfileId': content['qualityProfileId'],
            'titleSlug': content['titleSlug'],
            'tmdbId': content['tmdbId'],
            'year': content['year'],
            'monitored': content['monitored'],
            'minimumAvailability': 'released',
            'rootFolderPath': instanceB_path,
            'images': images,
            'profileId': instanceB_profile_id,
        }

def get_content_path(url, key):
    return '{0}/{1}?apikey={2}'.format(url, api_content_path, key)


def get_search_path(url, key):
     return '{0}/{1}?apikey={2}'.format(url, api_search_path, key)


def sync_content():

    # get sessions
    instanceA_session = requests.Session()
    instanceA_session.trust_env = False
    instanceA_content_url = get_content_path(instanceA_url, instanceA_key)
    instanceA_contents = instanceA_session.get(instanceA_content_url)
    if instanceA_contents.status_code != requests.codes.ok:
        logger.error('instanceA server error - response {}'.format(instanceA_contents.status_code))
        sys.exit(0)
    else:
        instanceA_contents = instanceA_contents.json()

    instanceB_session = requests.Session()
    instanceB_session.trust_env = False
    instanceB_content_url = get_content_path(instanceB_url, instanceB_key)
    instanceB_search_url = get_search_path(instanceA_url, instanceA_key)
    instanceB_contents = instanceB_session.get(instanceB_content_url)
    if instanceB_contents.status_code != requests.codes.ok:
        logger.error('instanceB server error - response {}'.format(instanceB_contents.status_code))
        sys.exit(0)
    else:
        instanceB_contents = instanceB_contents.json()


    # get all contentIds from instanceA so we can keep track of what contents already exist
    instanceB_contentIds = []
    for content_to_sync in instanceB_contents:
        instanceB_contentIds.append(content_to_sync[content_id_key])
    logger.debug('{} contents in instanceB'.format(len(instanceB_contentIds)))

    # sync content from instanceA to instanceB
    search_ids = []
    logger.info('syncing content')
    for content in instanceA_contents:

        # if content from A is not in B then sync
        if content[content_id_key] not in instanceB_contentIds:
                logging.info('syncing content title "{0}"'.format(content['title']))

                # get any images from the content
                images = content['images']
                for image in images:
                    image['url'] = '{0}{1}'.format(instanceB_url, image['url'])
                    logging.debug(image['url'])

                payload = get_new_content_payload(content, images)
                logger.debug(payload)

                sync_response = instanceB_session.post(instanceB_content_url, data=json.dumps(payload))
                if sync_response.status_code != 201 and sync_response.status_code != 200:
                    logger.error('server sync error for {} - response {}'.format(content['title'], sync_response.status_code))
                else:
                    search_ids.append(int(sync_response.json()['id']))
                    logging.info('content title "{0}" synced successfully'.format(content['title']))


    # now that we've synced all contents search for the newly synced contents
    logging.info('{} contents synced successfully'.format(len(search_ids)))
    if len(search_ids):
        payload = { 'name': 'contentsSearch', 'contentIds': search_ids }
        instanceB_session.post(instanceB_search_url, data=json.dumps(payload))


if is_in_docker:
    logger.info('syncing every {} seconds'.format(instance_sync_interval_seconds))

sync_content()

if is_in_docker:
    while True:
        time.sleep(instance_sync_interval_seconds)
        sync_content()

