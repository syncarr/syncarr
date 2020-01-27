#!/usr/bin/env python

import os
import logging
import requests
import json
import configparser
import sys
import time

from config import (
    instanceA_url, instanceA_key,  instanceA_path, instanceA_profile,
    instanceA_profile_id, instanceA_profile_filter, instanceA_profile_filter_id,
    instanceA_language_id, instanceA_language,

    instanceB_url, instanceB_key, instanceB_path, instanceB_profile,
    instanceB_profile_id, instanceB_profile_filter, instanceB_profile_filter_id,
    instanceB_language_id, instanceB_language,

    content_id_key, logger, is_sonarr, is_radarr, is_lidarr,
    get_status_path, get_content_path, get_search_path, get_profile_path, get_language_path,

    is_in_docker, instance_sync_interval_seconds, 
    sync_bidirectionally, auto_search, monitor_new_content,
    tested_api_version, api_version, V3_API_PATH,
)


def get_new_content_payload(content, instance_path, instance_profile_id, instance_url, instance_language_id=None):
    global monitor_new_content

    images = content.get('images')
    for image in images:
        image['url'] = '{0}{1}'.format(instance_url, image.get('url'))

    monitored = content.get('monitored')
    if monitor_new_content is not None:
        monitored = True if monitor_new_content else False

    payload = {
        content_id_key: content.get(content_id_key),
        'qualityProfileId': instance_profile_id or content.get('qualityProfileId'),
        'monitored': monitored,
        'rootFolderPath': instance_path,
        'images': images,
    }

    if is_sonarr:
        payload['title'] = content.get('title')
        payload['titleSlug'] = content.get('titleSlug')
        payload['seasons'] = content.get('seasons')
        payload['year'] = content.get('year')
        payload['tvRageId'] = content.get('tvRageId')
        payload['seasonFolder'] = content.get('seasonFolder')
        payload['languageProfileId'] = instance_language_id if instance_language_id is not None else content.get(
            'languageProfileId')
        payload['tags'] = content.get('tags')
        payload['seriesType'] = content.get('seriesType')
        payload['useSceneNumbering'] = content.get('useSceneNumbering')
        payload['addOptions'] = content.get('addOptions')

    elif is_radarr:
        payload['title'] = content.get('title')
        payload['year'] = content.get('year')
        payload['tmdbId'] = content.get('tmdbId')
        payload['titleSlug'] = content.get('titleSlug')

    elif is_lidarr:
        payload['artistName'] = content.get('artistName')
        payload['addOptions'] = content.get('addOptions', {})
        payload['albumFolder'] = content.get('albumFolder')
        payload['metadataProfileId'] = content.get('metadataProfileId')

    logger.debug(payload)
    return payload


def get_profile_from_id(instance_session, instance_url, instance_key, instance_profile, instance_name=''):
    instance_profile_url = get_profile_path(instance_url, instance_key)
    profiles_response = instance_session.get(instance_profile_url)
    if profiles_response.status_code != 200:
        logger.error(
            f'Could not get profile id from {instance_profile_url}')
        sys.exit(0)

    instance_profiles = None
    try:
        instance_profiles = profiles_response.json()
    except:
        logger.error(
            f'Could not decode profile id from {instance_profile_url}')
        sys.exit(0)

    profile = next((item for item in instance_profiles if item["name"].lower() == instance_profile.lower()), False)
    if not profile:
        logger.error('Could not find profile_id for instance {} profile {}'.format(
            instance_name, instance_profile))
        sys.exit(0)

    instance_profile_id = profile.get('id')
    logger.debug(
        f'found profile_id ({instance_name})" {instance_profile_id}" from profile "{instance_profile}"')

    return instance_profile_id


def get_language_from_id(instance_session, instance_url, instance_key, instance_language, instance_name=''):
    instance_language_url = get_language_path(instance_url, instance_key)
    language_response = instance_session.get(instance_language_url)
    if language_response.status_code != 200:
        logger.error(
            f'Could not get language id from ({instance_name}) {instance_language_url} - only works on sonarr v3')
        sys.exit(0)

    instance_languages = None
    try:
        instance_languages = language_response.json()
    except:
        logger.error(
            f'Could not decode language id from {instance_language_url}')
        sys.exit(0)

    instance_languages = instance_languages[0]['languages']
    language = next((item for item in instance_languages 
                     if item.get('language', {}).get('name').lower() == instance_language.lower()), False)

    logger.error(language)
    if not language:
        logger.error(f'Could not find language_id for instance {instance_name} and language {instance_language}')
        sys.exit(0)

    instance_language_id = language.get('language', {}).get('id')
    logger.debug(f'found id "{instance_language_id}" from language "{instance_language}" for instance {instance_name}')
    
    if instance_language_id is None:
        logger.error(f'language_id is None for instance {instance_name} and language {instance_language}')
        sys.exit(0)

    return instance_language_id


def search_synced(search_ids, instance_search_url, instance_session):
    # now that we've synced all contents search for the newly synced contents
    instance_search_url = get_search_path(instanceA_url, instanceA_key)

    if len(search_ids):
        payload = { 'name': 'contentsSearch', 'contentIds': search_ids }
        instance_session.post(instance_search_url, data=json.dumps(payload))


def sync_servers(instanceA_contents, instanceB_language_id, instanceB_contentIds,
                 instanceB_path, instanceB_profile_id, instanceB_session, 
                 instanceB_url, profile_filter_id, instanceB_key):
    global auto_search
    search_ids = []

    # if given instance A profile id then we want to filter out content without that id
    if profile_filter_id:
        logging.info('only filtering content from instance with profile_filter_id "{0}"'.format(profile_filter_id))

    # for each content id in instance A, check if it needs to be synced to instance B
    for content in instanceA_contents:
        if content[content_id_key] not in instanceB_contentIds:

            # if given this, we want to filter from instance A by profile id
            if profile_filter_id:
                if profile_filter_id != content.get('qualityProfileId'): continue

            title = content.get('title') or content.get('artistName')
            logging.info('syncing content title "{0}"'.format(title))

            # get the POST payload and sync content to instance B
            payload = get_new_content_payload(
                content=content, 
                instance_path=instanceB_path, 
                instance_profile_id=instanceB_profile_id, 
                instance_url=instanceB_url, 
                instance_language_id=instanceA_language_id,
            )
            instanceB_content_url = get_content_path(instanceB_url, instanceB_key)
            sync_response = instanceB_session.post(instanceB_content_url, data=json.dumps(payload))

            # check respons and save content id for searching later on if success
            if sync_response.status_code != 201 and sync_response.status_code != 200:
                logger.error('server sync error for {} - response {}'.format(title, sync_response.status_code))
            else:
                try:
                    search_ids.append(int(sync_response.json()['id']))
                except:
                    logger.error(f'Could not decode sync response from {instanceB_content_url}')
                logging.info('content title "{0}" synced successfully'.format(title))
    
    logging.info('{0} contents synced successfully'.format(len(search_ids)))
    instanceB_search_url = get_search_path(instanceB_url, instanceB_key)

    if auto_search:
        search_synced(search_ids, instanceB_search_url, instanceB_session)


def get_instance_contents(instance_url, instance_key, instance_session, instance_name=''):
    instance_contentIds = []

    instance_content_url = get_content_path(instance_url, instance_key)
    instance_contents = instance_session.get(instance_content_url)

    if instance_contents.status_code != 200:
        logger.error('instance{} server error - response {}'.format(instance_name, instance_contents.status_code))
        sys.exit(0)
    else:
        try:
            instance_contents = instance_contents.json()
        except:
            logger.error(f'Could not decode contents from {instance_content_url}')
            sys.exit(0)

    for content_to_sync in instance_contents:
        instance_contentIds.append(content_to_sync[content_id_key])

    logger.debug('{} contents in instance{}'.format(len(instance_contentIds), instance_name))
    return instance_contents, instance_contentIds


def check_status(instance_session, instance_url, instance_key, instance_name='', changed_api_version=False):
    global api_version

    instance_status_url = get_status_path(
        instance_url, instance_key, changed_api_version)
    error_message = f'Could not connect to instance{instance_name}: {instance_status_url}'
    status_response = None

    try:
        status_response = instance_session.get(instance_status_url)

        # only test again if not lidarr and we haven't tested v3 already
        if status_response.status_code != 200 and not changed_api_version and not is_lidarr:
            logger.debug(f'check api_version again')
            status_response = check_status(instance_session, instance_url, instance_key, instance_name, True)
        elif status_response.status_code != 200:
            logger.error(error_message)
            sys.exit(0)

    except:
        if not changed_api_version and not is_lidarr:
            logger.debug(f'check api_version again exception')
            status_response = check_status(
                instance_session, instance_url, instance_key, instance_name, True)

    if status_response is None:
        logger.error(error_message)
        sys.exit(0)
    else:
        try:
            status_response = status_response.json()
        except Exception as error:
            if not isinstance(status_response, dict):
                logger.error(
                    f"Could not retrieve status for {instance_status_url}: {status_response} - {error}")
                sys.exit(0)

        if(status_response.get('error')):
            logger.error(f"{instance_status_url} error {status_response.get('error')}")
            sys.exit(0)

        logger.debug(f"{instance_status_url} version {status_response.get('version')}")
    
    return status_response


def sync_content():
    global instanceA_profile_id, instanceA_profile, instanceB_profile_id, instanceB_profile, instanceA_profile_filter, instanceA_profile_filter_id, instanceB_profile_filter, instanceB_profile_filter_id, tested_api_version, instanceA_language_id, instanceA_language, instanceB_language_id, instanceB_language

    # get sessions
    instanceA_session = requests.Session()
    instanceA_session.trust_env = False
    instanceB_session = requests.Session()
    instanceB_session.trust_env = False

    if not tested_api_version:
        check_status(instanceA_session, instanceA_url, instanceA_key, instance_name='A')
        check_status(instanceB_session, instanceB_url, instanceB_key, instance_name='B')
        tested_api_version = True
            
    # if given a profile instead of a profile id then try to find the profile id
    if not instanceA_profile_id and instanceA_profile:
        instanceA_profile_id = get_profile_from_id(
            instanceA_session, instanceA_url, instanceA_key, instanceA_profile, 'A')
    if not instanceB_profile_id and instanceB_profile:
        instanceB_profile_id = get_profile_from_id(
            instanceB_session, instanceB_url, instanceB_key, instanceB_profile, 'B')
    logger.debug({
        'instanceA_profile_id': instanceA_profile_id,
        'instanceA_profile': instanceA_profile,
        'instanceB_profile_id': instanceB_profile_id,
        'instanceB_profile': instanceB_profile,
    })

    # if given language instead of language id then try to find the lanaguage id
    # only for sonarr v3
    if is_sonarr:
        if not instanceA_language_id and instanceA_language:
            instanceA_language_id = get_language_from_id(
                instance_session=instanceA_session, 
                instance_url=instanceA_url, 
                instance_key=instanceA_key, 
                instance_language=instanceA_language, 
                instance_name='A'
            )

        if not instanceB_language_id and instanceB_language:
            instanceB_language_id = get_language_from_id(
                instance_session=instanceB_session, 
                instance_url=instanceB_url, 
                instance_key=instanceB_key, 
                instance_language=instanceB_language, 
                instance_name='B'
            )
    
    logger.debug({
        'instanceA_language_id': instanceA_language_id,
        'instanceA_language': instanceA_language,
        'instanceB_language_id': instanceB_language_id,
        'instanceB_language': instanceB_language,
        'is_sonarr': is_sonarr,
        'api_version': api_version,
    })

    # get contents to compare
    instanceA_contents, instanceA_contentIds = get_instance_contents(instanceA_url, instanceA_key, instanceA_session, instance_name='A')
    instanceB_contents, instanceB_contentIds = get_instance_contents(instanceB_url, instanceB_key, instanceB_session, instance_name='B')

    logger.info('syncing content from instance A to instance B')
    sync_servers(
        instanceA_contents=instanceA_contents, 
        instanceB_contentIds=instanceB_contentIds, 
        instanceB_language_id=instanceB_language_id,
        instanceB_path=instanceB_path, 
        instanceB_profile_id=instanceB_profile_id, 
        instanceB_session=instanceB_session, 
        instanceB_url=instanceB_url, 
        profile_filter_id=instanceA_profile_filter_id,
        instanceB_key=instanceB_key,
    )

    # if given bidirectional flag then sync from instance B to instance A
    if sync_bidirectionally:
        logger.info('syncing content from instance B to instance A')

        sync_servers(
            instanceA_contents=instanceB_contents, 
            instanceB_contentIds=instanceA_contentIds, 
            instanceB_language_id=instanceA_language_id,
            instanceB_path=instanceA_path, 
            instanceB_profile_id=instanceA_profile_id, 
            instanceB_session=instanceA_session, 
            instanceB_url=instanceA_url, 
            profile_filter_id=instanceB_profile_filter_id,
            instanceB_key=instanceA_key,
        )

########################################################################################################################

if is_in_docker:
    logger.info('syncing every {} seconds'.format(instance_sync_interval_seconds))

sync_content()

if is_in_docker:
    while True:
        time.sleep(instance_sync_interval_seconds)
        sync_content()
