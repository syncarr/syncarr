from syncarr.config import *


def get_path(instance_url, api_path, key, checkV3=False):
    global api_version, api_profile_path
    logger.debug(f'checkV3: "{checkV3}" for {instance_url}')
    if checkV3:
        api_version = 'v3/'

    if checkV3 and is_sonarr:
        api_profile_path = 'qualityprofile'

    url = f"{instance_url}/api/{api_version}{api_path}?apikey={key}"
    print(url)
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


def get_profile_path(instance_url, key):
    url = get_path(instance_url, api_profile_path, key)
    logger.debug('get_profile_path: {}'.format(url))
    return url
