#!/usr/bin/env python

import os
import logging
import requests
import json
import configparser
import sys
import time

from syncarr.config import *


def get_new_content_payload(content, instance_path, instance_profile_id, instanceB_url):

    images = content.get('images')
    for image in images:
        image['url'] = '{0}{1}'.format(instanceB_url, image.get('url'))

    payload = {
        content_id_key: content.get(content_id_key),
        'qualityProfileId': content.get('qualityProfileId'),
        'monitored': content.get('monitored'),
        'rootFolderPath': instance_path,
        'images': images
    }

    if is_sonarr:
        payload['title'] = content.get('title')
        payload['titleSlug'] = content.get('titleSlug')
        payload['seasons'] = content.get('seasons')
        payload['tvRageId'] = content.get('tvRageId')
        payload['seasonFolder'] = content.get('seasonFolder')
        payload['languageProfileId'] = content.get('languageProfileId')
        payload['tags'] = content.get('tags')
        payload['seriesType'] = content.get('seriesType')
        payload['useSceneNumbering'] = content.get('useSceneNumbering')
        payload['addOptions'] = content.get('addOptions')

    elif is_radarr:
        payload['title'] = content.get('title')
        payload['tmdbId'] = content.get('tmdbId')
        payload['titleSlug'] = content.get('titleSlug')
        payload['minimumAvailability'] = content.get('minimumAvailability')
        payload['year'] = content.get('year')
        payload['profileId'] = instance_profile_id
    
    elif is_lidarr:
        payload['artistName'] = content.get('artistName')
        payload['addOptions'] = content.get('addOptions', {})
        payload['albumFolder'] = content.get('albumFolder')
        payload['metadataProfileId'] = content.get('metadataProfileId')

    logger.debug(payload)
    return payload


def get_content_path(instance_url, key):
    url = '{0}/{1}?apikey={2}'.format(instance_url, api_content_path, key)
    logger.debug('get_content_path: {}'.format(url))
    return url


def get_search_path(instance_url, key):
    url = '{0}/{1}?apikey={2}'.format(instance_url, api_search_path, key)
    logger.debug('get_search_path: {}'.format(url))
    return url


def get_profile_path(instance_url, key):
    url = '{0}/{1}?apikey={2}'.format(instance_url, api_profile_path, key)
    logger.debug('get_profile_path: {}'.format(url))
    return url

def get_profile_from_id(instance_session, instance_url, instance_key, instance_profile, instance_name=''):
    instance_profile_url = get_profile_path(instance_url, instance_key)
    instance_profiles = instance_session.get(instance_profile_url)
    instance_profiles = instance_profiles.json()

    profile = next((item for item in instance_profiles if item["name"].lower() == instance_profile.lower()), False)
    if not profile:
        logger.error('Could not find profile_id for instance {} profile {}'.format(instance_name, instance_profile))
        sys.exit(0)

    instance_profile_id = profile.get('id')
    logger.debug('found profile_id "{}" from profile "{}" for instance {}'.format(instance_profile_id, instance_profile, instance_name))
    return instance_profile_id


def search_synced(search_ids, instance_search_url, instance_session):
    # now that we've synced all contents search for the newly synced contents
    
    instanceA_search_url = get_search_path(instanceA_url, instanceA_key)

    if len(search_ids):
        payload = { 'name': 'contentsSearch', 'contentIds': search_ids }
        instance_session.post(instance_search_url, data=json.dumps(payload))

def sync_servers(
    instanceA_contents, 
    instanceB_contentIds, 
    instanceB_path, 
    instanceB_profile_id, 
    instanceB_session, 
    instanceB_url, 
    profile_filter_id,
    instanceB_key,
):

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
            payload = get_new_content_payload(content, instanceB_path, instanceB_profile_id, instanceB_url)
            instanceB_content_url = get_content_path(instanceB_url, instanceB_key)
            sync_response = instanceB_session.post(instanceB_content_url, data=json.dumps(payload))

            # check respons and save content id for searching later on if success
            if sync_response.status_code != 201 and sync_response.status_code != 200:
                logger.error('server sync error for {} - response {}'.format(title, sync_response.status_code))
            else:
                search_ids.append(int(sync_response.json()['id']))
                logging.info('content title "{0}" synced successfully'.format(title))
    
    logging.info('{0} contents synced successfully'.format(len(search_ids)))
    instanceB_search_url = get_search_path(instanceB_url, instanceB_key)
    search_synced(search_ids, instanceB_search_url, instanceB_session)


def get_instance_contents(instance_url, instance_key, instance_session, instance_name=''):
    instance_contentIds = []

    instance_content_url = get_content_path(instance_url, instance_key)
    instance_contents = instance_session.get(instance_content_url)

    if instance_contents.status_code != requests.codes.ok:
        logger.error('instance{} server error - response {}'.format(instance_name, instance_contents.status_code))
        sys.exit(0)
    else:
        instance_contents = instance_contents.json()

    for content_to_sync in instance_contents:
        instance_contentIds.append(content_to_sync[content_id_key])

    logger.debug('{} contents in instance{}'.format(len(instance_contentIds), instance_name))
    return instance_contents, instance_contentIds


def sync_content():
    global instanceA_profile_id, instanceA_profile, instanceB_profile_id, instanceB_profile, instanceA_profile_filter, instanceA_profile_filter_id, instanceB_profile_filter, instanceB_profile_filter_id

    # get sessions
    instanceA_session = requests.Session()
    instanceA_session.trust_env = False
    instanceB_session = requests.Session()
    instanceB_session.trust_env = False
    
    # if given a profile instead of a profile id then try to find the profile id
    if not instanceA_profile_id and instanceA_profile:
        instanceA_profile_id = get_profile_from_id(instanceA_session, instanceA_url, instanceA_key, instanceA_profile, 'A')
    if not instanceB_profile_id and instanceB_profile:
        instanceB_profile_id = get_profile_from_id(instanceB_session, instanceB_url, instanceB_key, instanceB_profile, 'B')
    logger.debug({
        'instanceA_profile_id': instanceA_profile_id,
        'instanceA_profile': instanceA_profile,
        'instanceA_profile_id': instanceA_profile_id,
        'instanceB_profile': instanceB_profile,
    })

    # if given profile filters then get ids
    if not instanceA_profile_id and instanceA_profile_filter:
        instanceA_profile_filter_id = get_profile_from_id(instanceA_session, instanceA_url, instanceA_key, instanceA_profile_filter, 'A')
    if not instanceB_profile_id and instanceB_profile_filter:
        instanceB_profile_filter_id = get_profile_from_id(instanceB_session, instanceB_url, instanceB_key, instanceB_profile_filter, 'B')
    logger.debug({
        'instanceA_profile_filter': instanceA_profile_filter,
        'instanceA_profile_filter_id': instanceA_profile_filter_id,
        'instanceB_profile_filter': instanceB_profile_filter,
        'instanceB_profile_filter_id': instanceB_profile_filter_id,
    })

    # get contents to compare
    instanceA_contents, instanceA_contentIds = get_instance_contents(instanceA_url, instanceA_key, instanceA_session, instance_name='A')
    instanceB_contents, instanceB_contentIds = get_instance_contents(instanceB_url, instanceB_key, instanceB_session, instance_name='B')

    logger.info('syncing content from instance A to instance B')
    search_ids = sync_servers(
        instanceA_contents=instanceA_contents, 
        instanceB_contentIds=instanceB_contentIds, 
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

        search_ids = sync_servers(
            instanceA_contents=instanceB_contents, 
            instanceB_contentIds=instanceA_contentIds, 
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
