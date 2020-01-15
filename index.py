#!/usr/bin/env python

import os
import logging
import requests
import json
import configparser
import sys
import time

DEV = False
VER = '1.0.0'

# load config file
if DEV:
    settingsFilename = os.path.join(os.getcwd(), 'dev-Config.txt')
else:
    settingsFilename = os.path.join(os.getcwd(), 'Config.txt')

Config = configparser.ConfigParser()
Config.read(settingsFilename)

is_in_docker = os.environ.get('IS_IN_DOCKER')
radarr_sync_interval_seconds = int(os.environ.get('SYNC_INTERVAL_SECONDS'))

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

def get_config_value(env_key, config_key, config_section, required=False):
    value = ''
    config = ConfigSectionMap(config_section)

    if is_in_docker:
        value = os.environ.get(env_key)
    else:
        value = config.get(config_key)

    if required and not value:
        key = env_key if is_in_docker else config_key
        logger.error('config var "{}" is required'.format(key))
        sys.exit(0)

    return value


# get config settings from ENV or config files
radarrA_url = get_config_value('RADARR_A_URL', 'url', 'radarrA', True)
radarrA_key = get_config_value('RADARR_A_KEY', 'key', 'radarrA', True)
radarrA_profile = get_config_value('RADARR_A_PROFILE', 'profile', 'radarrA')
radarrA_profile_id = get_config_value('RADARR_A_PROFILE_ID', 'profile_id', 'radarrA')
radarrA_path = get_config_value('RADARR_A_PATH', 'path', 'radarrA')

radarrB_url = get_config_value('RADARR_B_URL', 'url', 'radarrB', True)
radarrB_key = get_config_value('RADARR_B_KEY', 'key', 'radarrB', True)
radarrB_profile = get_config_value('RADARR_B_PROFILE', 'profile', 'radarrB')
radarrB_profile_id = get_config_value('RADARR_B_PROFILE_ID', 'profile_id', 'radarrB', True)
radarrB_path = get_config_value('RADARR_B_PATH', 'path', 'radarrB', True)


def sync_movies():

    # get radarr sessions
    radarrA_session = requests.Session()
    radarrA_session.trust_env = False
    radarrA_movies = radarrA_session.get('{0}/api/movie?apikey={1}'.format(radarrA_url, radarrA_key))
    if radarrA_movies.status_code != requests.codes.ok:
        logger.error('RadarrA server error - response {}'.format(radarrA_movies.status_code))
        sys.exit(0)
    else:
        radarrA_movies = radarrA_movies.json()

    radarrB_session = requests.Session()
    radarrB_session.trust_env = False
    radarrB_movies = radarrB_session.get('{0}/api/movie?apikey={1}'.format(radarrB_url, radarrB_key))
    if radarrB_movies.status_code != requests.codes.ok:
        logger.error('RadarrB server error - response {}'.format(radarrB_movies.status_code))
        sys.exit(0)
    else:
        radarrB_movies = radarrB_movies.json()


    # get all tmdbIds from radarrA so we can keep track of what movies already exist
    radarrB_tmdbIds = []
    for movie_to_sync in radarrB_movies:
        radarrB_tmdbIds.append(movie_to_sync['tmdbId'])
    logger.debug('{} movies in radarrB'.format(len(radarrB_tmdbIds)))

    # sync movies from radarrA to radarrB
    searchids = []
    logger.info('syncing movies')
    for movie in radarrA_movies:

        # if movie from A is not in B then sync
        if movie['tmdbId'] not in radarrB_tmdbIds:
                logging.info('syncing movie title "{0}"'.format(movie['title']))

                # get any images from the movie
                images = movie['images']
                for image in images:
                    image['url'] = '{0}{1}'.format(radarrB_url, image['url'])
                    logging.debug(image['url'])

                payload = {
                    'title': movie['title'],
                    'qualityProfileId': movie['qualityProfileId'],
                    'titleSlug': movie['titleSlug'],
                    'tmdbId': movie['tmdbId'],
                    'year': movie['year'],
                    'monitored': movie['monitored'],
                    'minimumAvailability': 'released',
                    'rootFolderPath': radarrB_path,
                    'images': images,
                    'profileId': radarrB_profile_id,
                }

                logger.debug(payload)

                sync_response = radarrB_session.post('{0}/api/movie?apikey={1}'.format(radarrB_url, radarrB_key), data=json.dumps(payload))
                if sync_response.status_code != 201:
                    logger.error('server sync error for {} - response {}'.format(movie['title'], sync_response.status_code))
                else:
                    searchids.append(int(sync_response.json()['id']))
                    logging.info('movie title "{0}" synced successfully'.format(movie['title']))


    # now that we've synced all movies search for the newly synced movies
    logging.info('{} movies synced successfully'.format(len(searchids)))
    if len(searchids):
        payload = { 'name': 'MoviesSearch', 'movieIds': searchid }
        radarrB_session.post('{0}/api/command?apikey={1}'.format(SyncServer_url, SyncServer_key), data=json.dumps(payload))


if is_in_docker:
    logger.info('syncing every {} seconds'.format(radarr_sync_interval_seconds))

sync_movies()

if is_in_docker:
    while True:
        time.sleep(radarr_sync_interval_seconds)
        sync_movies()
