#!/usr/bin/env python

import os
import logging
import requests
import json
import configparser
import sys
import time
import re
from os.path import dirname

from config import (
    instanceA_url, instanceA_key,  instanceA_path, instanceA_profile,
    instanceA_profile_id, instanceA_profile_filter, instanceA_profile_filter_id,
    instanceA_language_id, instanceA_language, instanceA_quality_match,
    instanceA_tag_filter_id, instanceA_tag_filter, instanceA_blacklist,

    instanceB_url, instanceB_key, instanceB_path, instanceB_profile,
    instanceB_profile_id, instanceB_profile_filter, instanceB_profile_filter_id,
    instanceB_language_id, instanceB_language, instanceB_quality_match,
    instanceB_tag_filter_id, instanceB_tag_filter, instanceB_blacklist,

    content_id_key, logger, is_sonarr, is_radarr, is_lidarr,
    get_status_path, get_content_path, get_profile_path, get_language_path, get_tag_path, get_content_put_path,

    is_in_docker, instance_sync_interval_seconds,
    sync_bidirectionally, auto_search, skip_missing, monitor_new_content,
    api_version, is_test_run, sync_monitor
)


def get_content_details(content, instance_path, instance_profile_id, instance_url, instance_language_id=None):
    """gets details of a content item"""
    global monitor_new_content, auto_search

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

    add_options = content.get('addOptions', {})
    search_missing = True if auto_search else False

    if is_sonarr:
        payload['title'] = content.get('title')
        payload['titleSlug'] = content.get('titleSlug')
        payload['seasons'] = content.get('seasons')
        payload['year'] = content.get('year')
        payload['tvRageId'] = content.get('tvRageId')
        payload['seasonFolder'] = content.get('seasonFolder')
        payload['languageProfileId'] = instance_language_id if instance_language_id else content.get(
            'languageProfileId')
        payload['tags'] = content.get('tags')
        payload['seriesType'] = content.get('seriesType')
        payload['useSceneNumbering'] = content.get('useSceneNumbering')
        payload['addOptions'] = {
            **add_options,
            **{'searchForMissingEpisodes': search_missing}
        }

    elif is_radarr:
        payload['title'] = content.get('title')
        payload['year'] = content.get('year')
        payload['tmdbId'] = content.get('tmdbId')
        payload['titleSlug'] = content.get('titleSlug')
        payload['addOptions'] = {
            **add_options,
            **{'searchForMovie': search_missing}
        }

    elif is_lidarr:
        payload['artistName'] = content.get('artistName')
        payload['albumFolder'] = content.get('albumFolder')
        payload['metadataProfileId'] = content.get('metadataProfileId')
        payload['addOptions'] = {
            **add_options,
            **{
                "monitored": monitored,
                "searchForMissingAlbums": search_missing
            }
        }

    logger.debug(payload)
    return payload


def get_quality_profiles(instance_session, instance_url, instance_key):
    instance_profile_url = get_profile_path(instance_url, instance_key)
    profiles_response = instance_session.get(instance_profile_url)
    if profiles_response.status_code != 200:
        logger.error(f'Could not get profile id from {instance_profile_url}')
        exit_system()

    instance_profiles = None
    try:
        instance_profiles = profiles_response.json()
        return instance_profiles
    except:
        logger.error(f'Could not decode profile id from {instance_profile_url}')
        exit_system()


def get_profile_from_id(instance_session, instance_url, instance_key, instance_profile, instance_name=''):
    instance_profiles = get_quality_profiles(instance_session=instance_session, instance_url=instance_url, instance_key=instance_key)

    profile = next((item for item in instance_profiles if item["name"].lower() == instance_profile.lower()), False)
    if not profile:
        logger.error('Could not find profile_id for instance {} profile {}'.format(instance_name, instance_profile))
        exit_system()

    instance_profile_id = profile.get('id')
    logger.debug(f'found profile_id (instance{instance_name}) "{instance_profile_id}" from profile "{instance_profile}"')

    return instance_profile_id


def get_tag_from_id(instance_session, instance_url, instance_key, instance_tag, instance_name=''):
    instance_tag_url = get_tag_path(instance_url, instance_key)
    tag_response = instance_session.get(instance_tag_url)
    if tag_response.status_code != 200:
        logger.error(f'Could not get tag id from (instance{instance_name}) {instance_tag_url} - only works on Sonarr')
        exit_system()

    instance_tags = None
    try:
        instance_tags = tag_response.json()
    except:
        logger.error(f'Could not decode tag id from {instance_tag_url}')
        exit_system()

    tag_ids = []
    for item in instance_tags:
        for instance_item in instance_tag:
            if item.get('label').lower() == instance_item.lower():
                tag_ids.append(item)

    if not tag_ids:
        logger.error(f'Could not find tag_id for instance {instance_name} and tag {instance_tags}')
        exit_system()

    instance_tag_ids = [tag.get('id') for tag in tag_ids]
    logger.debug(f'found id "{instance_tag_ids}" from tag "{instance_tag}" for instance {instance_name}')

    if instance_tag_ids is None:
        logger.error(f'tag_id is None for instance {instance_name} and tag {instance_tag}')
        exit_system()

    return instance_tag_ids


def get_language_from_id(instance_session, instance_url, instance_key, instance_language, instance_name=''):
    instance_language_url = get_language_path(instance_url, instance_key)
    language_response = instance_session.get(instance_language_url)
    if language_response.status_code != 200:
        logger.error(f'Could not get language id from (instance{instance_name}) {instance_language_url} - only works on sonarr v3')
        exit_system()

    instance_languages = None
    try:
        instance_languages = language_response.json()
    except:
        logger.error(f'Could not decode language id from {instance_language_url}')
        exit_system()

    instance_languages = instance_languages[0]['languages']
    language = next((item for item in instance_languages if item.get('language', {}).get('name').lower() == instance_language.lower()), False)

    if not language:
        logger.error(f'Could not find language_id for instance {instance_name} and language {instance_language}')
        exit_system()

    instance_language_id = language.get('language', {}).get('id')
    logger.debug(f'found id "{instance_language_id}" from language "{instance_language}" for instance {instance_name}')

    if instance_language_id is None:
        logger.error(f'language_id is None for instance {instance_name} and language {instance_language}')
        exit_system()

    return instance_language_id


def sync_servers(instanceA_contents, instanceB_language_id, instanceB_contentIds,
                 instanceB_path, instanceB_profile_id, instanceA_profile_filter_id,
                 instanceB_session, instanceB_url, instanceB_key, instanceA_quality_match,
                 instanceA_tag_filter_id, instanceA_blacklist, instanceB_contents):
    global is_radarr, is_sonarr, is_test_run, sync_monitor
    search_ids = []

    # if given instance A profile id then we want to filter out content without that id
    if instanceA_profile_filter_id:
        logging.info(f'only filtering content with instanceA_profile_filter_id {instanceA_profile_filter_id}')

    # for each content id in instance A, check if it needs to be synced to instance B
    for content in instanceA_contents:
        content_not_synced = content[content_id_key] not in instanceB_contentIds
        # only skip alrerady synced items if we arent syncing monitoring as well 
        if content_not_synced or sync_monitor:
            title = content.get('title') or content.get('artistName')
            instance_path = instanceB_path or dirname(content.get('path'))

            # if skipping missing files, we want to skip any that don't have files
            if skip_missing:
                content_has_file = content.get('hasFile')
                if not content_has_file:
                    logging.debug(f'Skipping content {title} - file missing')
                    continue

            # if given this, we want to filter from instance by profile id
            if instanceA_profile_filter_id:
                quality_profile_id = content.get('qualityProfileId')
                if instanceA_profile_filter_id != quality_profile_id:
                    logging.debug(f'Skipping content {title} - mismatched quality_profile_id {quality_profile_id} with instanceA_profile_filter_id {instanceA_profile_filter_id}')
                    continue

            # if given quality filter we want to filter if quality from instanceA isnt high enough yet
            if is_radarr and instanceA_quality_match:
                content_quality = content.get('movieFile', {}).get('quality', {}).get('quality', {}).get('name', '')
                if content_quality and not re.match(instanceA_quality_match, content_quality):
                    logging.debug(f'Skipping content {title} - mismatched content_quality {content_quality} with instanceA_quality_match {instanceA_quality_match}')
                    continue

            # if given tag filter then filter by tag - (Sonarr/Radarr v3 only)
            if (is_sonarr or is_radarr) and instanceA_tag_filter_id:
                content_tag_ids = content.get('tags')
                if not (set(content_tag_ids) & set(instanceA_tag_filter_id)):
                    logging.debug(f'Skipping content {title} - mismatched content_tag_ids {content_tag_ids} with instanceA_tag_filter_id {instanceA_tag_filter_id}')
                    continue

            # if black list given then dont sync matching slugs/ids
            if instanceA_blacklist:
                title_slug = content.get('titleSlug') or content.get('foreignArtistId')
                if title_slug in instanceA_blacklist:
                    logging.debug(f'Skipping content {title} - blacklist slug: {title_slug}')
                    continue

                content_id = str(content.get('id'))
                if content_id in instanceA_blacklist:
                    logging.debug(f'Skipping content {title} - blacklist ID: {content_id}')
                    continue


            # generate content from instance A to sync into instance B
            formatted_content = get_content_details(
                content=dict(content),
                instance_path=instance_path,
                instance_profile_id=instanceB_profile_id,
                instance_url=instanceB_url,
                instance_language_id=instanceB_language_id,
            )
            instanceB_content_url = get_content_path(instanceB_url, instanceB_key)

            if is_test_run:
                logging.info('content title "{0}" synced successfully (test only)'.format(title))
            elif content_not_synced:
                # sync content if not synced
                logging.info(f'syncing content title "{title}"')
                sync_response = instanceB_session.post(instanceB_content_url, data=json.dumps(formatted_content))
                # check response and save content id for searching later on if success
                if sync_response.status_code != 201 and sync_response.status_code != 200:
                    logger.error(f'server sync error for {title} - response: {sync_response.text}')
                else:
                    try:
                        search_ids.append(int(sync_response.json()['id']))
                    except:
                        logger.error(f'Could not decode sync response from {instanceB_content_url}')
                    logging.info('content title "{0}" synced successfully'.format(title))

            elif sync_monitor:
                # else if is already synced and we want to sync monitoring then sync that now
                
                # find matching content from instance B to check monitored status
                matching_content_instanceB = list(filter(lambda content_instanceB: content_instanceB['titleSlug'] == content.get('titleSlug'), instanceB_contents))
                if(len(matching_content_instanceB) == 1):
                    matching_content_instanceB = matching_content_instanceB[0]
                    # if we found a content match from instance B, then check monitored status - if different then sync from A to B
                    if matching_content_instanceB['monitored'] != content['monitored']:
                        matching_content_instanceB['monitored'] = content['monitored']
                        instanceB_content_url = get_content_put_path(instanceB_url, instanceB_key, matching_content_instanceB.get('id'))
                        sync_response = instanceB_session.put(instanceB_content_url, data=json.dumps(matching_content_instanceB))
                        # check response and save content id for searching later on if success
                        if sync_response.status_code != 202:
                            logger.error(f'server monitoring sync error for {title} - response: {sync_response.text}')
                        else:
                            try:
                                search_ids.append(int(sync_response.json()['id']))
                            except:
                                logger.error(f'Could not decode sync response from {instanceB_content_url}')
                            logging.info('content title "{0}" monitoring synced successfully'.format(title))

    logging.info(f'{len(search_ids)} contents synced successfully')


def get_instance_contents(instance_url, instance_key, instance_session, instance_name=''):
    instance_contentIds = []
    instance_content_url = get_content_path(instance_url, instance_key)
    instance_contents = instance_session.get(instance_content_url)

    if instance_contents.status_code != 200:
        logger.error('instance{} server error - response {}'.format(instance_name, instance_contents.status_code))
        exit_system()
    else:
        try:
            instance_contents = instance_contents.json()
        except:
            logger.error(f'Could not decode contents from {instance_content_url}')
            exit_system()

    for content_to_sync in instance_contents:
        instance_contentIds.append(content_to_sync[content_id_key])

    logger.debug('{} contents in instance {}'.format(len(instance_contentIds), instance_name))
    return instance_contents, instance_contentIds


def check_status(instance_session, instance_url, instance_key, instance_name=''):
    global api_version

    instance_status_url = get_status_path(instance_url, instance_key)
    error_message = f'Could not connect to instance{instance_name}: {instance_status_url}'
    status_response = None

    try:
        status_response = instance_session.get(instance_status_url)
        if status_response.status_code != 200:
            logger.error(error_message)
            exit_system()
    except:
        logger.error(error_message)
        exit_system()

    if status_response is None:
        logger.error(error_message)
        exit_system()
    else:
        try:
            status_response = status_response.json()
        except Exception as error:
            if not isinstance(status_response, dict):
                logger.error(
                    f"Could not retrieve status for {instance_status_url}: {status_response} - {error}")
                exit_system()

        if(status_response.get('error')):
            logger.error(f"{instance_status_url} error {status_response.get('error')}")
            exit_system()

        logger.debug(f"{instance_status_url} version {status_response.get('version')}")

    return status_response


def sync_content():
    global instanceA_profile_id, instanceA_profile, instanceB_profile_id, instanceB_profile, instanceA_profile_filter, instanceA_profile_filter_id, instanceB_profile_filter, instanceB_profile_filter_id, tested_api_version, instanceA_language_id, instanceA_language, instanceB_language_id, instanceB_language, instanceA_quality_match, instanceB_quality_match, is_sonarr, instanceA_tag_filter_id, instanceA_tag_filter, instanceB_tag_filter_id, instanceB_tag_filter, is_radarr, instanceA_blacklist, instanceB_blacklist

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
        'instanceB_profile_id': instanceB_profile_id,
        'instanceB_profile': instanceB_profile,
    })

    # do the same for profile id filters if they exist
    if not instanceA_profile_filter_id and instanceA_profile_filter:
        instanceA_profile_filter_id = get_profile_from_id(instanceA_session, instanceA_url, instanceA_key, instanceA_profile_filter, 'A')
    if not instanceB_profile_filter_id and instanceB_profile_filter:
        instanceB_profile_filter_id = get_profile_from_id(instanceB_session, instanceB_url, instanceB_key, instanceB_profile_filter, 'B')
    logger.debug({
        'instanceAprofile_filter_id': instanceA_profile_filter_id,
        'instanceAprofile_filter': instanceA_profile_filter,
        'instanceBprofile_filter_id': instanceB_profile_filter_id,
        'instanceBprofile_filter': instanceB_profile_filter,
    })

    # do the same for tag id filters if they exist - (only Sonarr)
    if is_sonarr or is_radarr:
        if not instanceA_tag_filter_id and instanceA_tag_filter:
            instanceA_tag_filter_id = get_tag_from_id(instanceA_session, instanceA_url, instanceA_key, instanceA_tag_filter, 'A')
        if not instanceB_tag_filter_id and instanceB_tag_filter:
            instanceB_tag_filter_id = get_tag_from_id(instanceB_session, instanceB_url, instanceB_key, instanceA_tag_filter, 'B')
        logger.debug({
            'instanceA_tag_filter': instanceA_tag_filter,
            'instanceA_profile_filter': instanceA_profile_filter,
            'instanceB_tag_filter_id': instanceB_tag_filter_id,
            'instanceB_tag_filter': instanceB_tag_filter,
        })

    # if given language instead of language id then try to find the lanaguage id - (only Sonarr v3)
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
        instanceB_contents=instanceB_contents,
        instanceB_contentIds=instanceB_contentIds,
        instanceB_language_id=instanceB_language_id,
        instanceB_path=instanceB_path,
        instanceB_profile_id=instanceB_profile_id,
        instanceB_session=instanceB_session,
        instanceB_url=instanceB_url,
        instanceA_profile_filter_id=instanceA_profile_filter_id,
        instanceB_key=instanceB_key,
        instanceA_quality_match=instanceA_quality_match,
        instanceA_tag_filter_id=instanceA_tag_filter_id,
        instanceA_blacklist=instanceA_blacklist
    )

    # if given bidirectional flag then sync from instance B to instance A
    if sync_bidirectionally:
        logger.info('syncing content from instance B to instance A')

        sync_servers(
            instanceA_contents=instanceB_contents,
            instanceB_contents=instanceA_contents,
            instanceB_contentIds=instanceA_contentIds,
            instanceB_language_id=instanceA_language_id,
            instanceB_path=instanceA_path,
            instanceB_profile_id=instanceA_profile_id,
            instanceB_session=instanceA_session,
            instanceB_url=instanceA_url,
            instanceA_profile_filter_id=instanceB_profile_filter_id,
            instanceB_key=instanceA_key,
            instanceA_quality_match=instanceB_quality_match,
            instanceA_tag_filter_id=instanceB_tag_filter_id,
            instanceA_blacklist=instanceB_blacklist
        )

########################################################################################################################


def exit_system():
    """we dont want to exit if in docker"""
    if is_in_docker:
        raise Exception
    else:
        sys.exit(0)


if is_in_docker:
    logger.info('syncing every {} seconds'.format(instance_sync_interval_seconds))

sync_content()

if is_in_docker:
    while True:
        try:
            time.sleep(instance_sync_interval_seconds)
            sync_content()
        except Exception as inst:
            d = inst
