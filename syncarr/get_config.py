import os
import configparser


DEV = os.environ.get('DEV', False)
VER = '1.3.0'


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
# get docker based ENV vars
is_in_docker = os.environ.get('IS_IN_DOCKER')
instance_sync_interval_seconds = os.environ.get('SYNC_INTERVAL_SECONDS')
if instance_sync_interval_seconds:
    instance_sync_interval_seconds = int(instance_sync_interval_seconds)

########################################################################################################################
# get config settings from ENV or config files for Radarr
radarrA_url = get_config_value('RADARR_A_URL', 'url', 'radarrA')
radarrA_key = get_config_value('RADARR_A_KEY', 'key', 'radarrA')
radarrA_profile = get_config_value('RADARR_A_PROFILE', 'profile', 'radarrA')
radarrA_profile_id = get_config_value('RADARR_A_PROFILE_ID', 'profile_id', 'radarrA')
radarrA_profile_filter = get_config_value('RADARR_A_PROFILE_FILTER', 'profile_filter', 'radarrA')
radarrA_profile_filter_id = get_config_value('RADARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'radarrA')
radarrA_path = get_config_value('RADARR_A_PATH', 'path', 'radarrA')

radarrB_url = get_config_value('RADARR_B_URL', 'url', 'radarrB')
radarrB_key = get_config_value('RADARR_B_KEY', 'key', 'radarrB')
radarrB_profile = get_config_value('RADARR_B_PROFILE', 'profile', 'radarrB')
radarrB_profile_id = get_config_value('RADARR_B_PROFILE_ID', 'profile_id', 'radarrB')
radarrB_profile_filter = get_config_value('RADARR_B_PROFILE_FILTER', 'profile_filter', 'radarrB')
radarrB_profile_filter_id = get_config_value('RADARR_B_PROFILE_FILTER_ID', 'profile_filter_id', 'radarrB')
radarrB_path = get_config_value('RADARR_B_PATH', 'path', 'radarrB')

# get config settings from ENV or config files for Sonarr
sonarrA_url = get_config_value('SONARR_A_URL', 'url', 'sonarrA')
sonarrA_key = get_config_value('SONARR_A_KEY', 'key', 'sonarrA')
sonarrA_profile = get_config_value('SONARR_A_PROFILE', 'profile', 'sonarrA')
sonarrA_profile_id = get_config_value('SONARR_A_PROFILE_ID', 'profile_id', 'sonarrA')
sonarrA_profile_filter = get_config_value('SONARR_A_PROFILE_FILTER', 'profile_filter', 'sonarrA')
sonarrA_profile_filter_id = get_config_value('SONARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'sonarrA')
sonarrA_path = get_config_value('SONARR_A_PATH', 'path', 'sonarrA')

sonarrB_url = get_config_value('SONARR_B_URL', 'url', 'sonarrB')
sonarrB_key = get_config_value('SONARR_B_KEY', 'key', 'sonarrB')
sonarrB_profile = get_config_value('SONARR_B_PROFILE', 'profile', 'sonarrB')
sonarrB_profile_id = get_config_value('SONARR_B_PROFILE_ID', 'profile_id', 'sonarrB')
sonarrB_profile_filter = get_config_value('SONARR_A_PROFILE_FILTER', 'profile_filter', 'sonarrB')
sonarrB_profile_filter_id = get_config_value('SONARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'sonarrB')
sonarrB_path = get_config_value('SONARR_B_PATH', 'path', 'sonarrB')

# get config settings from ENV or config files for Lidarr
lidarrA_url = get_config_value('LIDARR_A_URL', 'url', 'lidarrA')
lidarrA_key = get_config_value('LIDARR_A_KEY', 'key', 'lidarrA')
lidarrA_profile = get_config_value('LIDARR_A_PROFILE', 'profile', 'lidarrA')
lidarrA_profile_id = get_config_value('LIDARR_A_PROFILE_ID', 'profile_id', 'lidarrA')
lidarrA_profile_filter = get_config_value('LIDARR_A_PROFILE_FILTER', 'profile_filter', 'lidarrA')
lidarrA_profile_filter_id = get_config_value('LIDARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'lidarrA')
lidarrA_path = get_config_value('LIDARR_A_PATH', 'path', 'lidarrA')

lidarrB_url = get_config_value('LIDARR_B_URL', 'url', 'lidarrB')
lidarrB_key = get_config_value('LIDARR_B_KEY', 'key', 'lidarrB')
lidarrB_profile = get_config_value('LIDARR_B_PROFILE', 'profile', 'lidarrB')
lidarrB_profile_id = get_config_value('LIDARR_B_PROFILE_ID', 'profile_id', 'lidarrB')
lidarrB_profile_filter = get_config_value('LIDARR_A_PROFILE_FILTER', 'profile_filter', 'lidarrB')
lidarrB_profile_filter_id = get_config_value('LIDARR_A_PROFILE_FILTER_ID', 'profile_filter_id', 'lidarrB')
lidarrB_path = get_config_value('LIDARR_B_PATH', 'path', 'lidarrB')

# get general conf options
sync_bidirectionally = get_config_value('SYNCARR_BIDIRECTIONAL_SYNC', 'bidirectional', 'general') or 0
if sync_bidirectionally:
    sync_bidirectionally = int(sync_bidirectionally) or 0