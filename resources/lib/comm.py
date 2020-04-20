import base64
import classes
import config
import json
import uuid

from aussieaddonscommon import session
from aussieaddonscommon import utils

import xbmcaddon

import xbmcgui


def clear_login_token(show_dialog=True):
    addon = xbmcaddon.Addon()
    addon.setSetting('user_token', '')
    addon.setSetting('unique_id', '')
    addon.setSetting('ad_id', '')
    if show_dialog:
        utils.dialog_message('Login token cleared. Ensure you press OK in '
                             'the settings to save this change.')


def get_login_token():
    addon = xbmcaddon.Addon()
    encoded_token = addon.getSetting('user_token')
    if encoded_token:
        return encoded_token
    addon.setSetting('unique_id', str(uuid.uuid4()))
    addon.setSetting('ad_id', str(uuid.uuid4()))
    username = xbmcgui.Dialog().input('Enter SBS on Demand username/email',
                                      type=xbmcgui.INPUT_ALPHANUM)
    if not username:
        return False
    password = xbmcgui.Dialog().input('Enter SBS on Demand password',
                                      type=xbmcgui.INPUT_ALPHANUM,
                                      option=xbmcgui.ALPHANUM_HIDE_INPUT)
    if not password:
        return False
    upresp = fetch_url(config.LOGIN1_URL, data={'context': 'android',
                                                'device': 'phone',
                                                'version': '3.2.1',
                                                'loginVersion': '1.0.0',
                                                'user': username,
                                                'pass': password,
                                                'express': '0'})
    upresp_json = json.loads(upresp)
    if upresp_json.get('error', '') == 'invalid_credentials':
        utils.dialog_message('Invalid username or password. Please check and '
                             'try again.')
        return False
    access_token = upresp_json.get('access_token')
    ## insert check for email validation??
    atresp = fetch_url(config.LOGIN2_URL.format(token=access_token))
    session_id = json.loads(atresp)['completelogin']['response'].get(
        'sessionid')
    encoded_token = base64.b64encode('{0}:android'.format(session_id))
    addon.setSetting('user_token', encoded_token)
    return encoded_token


def fetch_url(url, headers=None, data=None):
    """Simple function that fetches a URL using requests."""
    with session.Session() as sess:
        if headers:
            sess.headers.update(headers)
        if data:
            request = sess.post(url, data=data)
        else:
            request = sess.get(url)
        res = request.text
    return res


def fetch_protected_url(url, token):
    """For protected URLs we add or Auth header when fetching"""
    headers = {'Authorization': 'Basic ' + token}
    return fetch_url(url, headers)


def get_index():
    """Fetch the main index.

    This contains a mix of actual program information
    and URL references to other queries which return programs
    """
    resp = fetch_url(config.CONFIG_URL)
    json_data = json.loads(resp)
    return json_data


def get_category(params):
    """Fetch a given top level category from the index.
    This is usually programs and movies.
    """
    sub_cat = False
    category = params.get('category')
    if not category:
        sub_cat = True
        category = params.get('item_type')  # genre
        if category == 'FilmGenre':
            category = 'MovieGenre'
    utils.log("Fetching category: %s" % category)
    resp = fetch_url(config.CONFIG_URL)
    json_data = json.loads(resp)
    category_data = json_data.get(
        'contentStructure').get('screens').get(category)
    listing = []

    for c in category_data.get('rows'):

        if 'feeds' in c:
            data_list = c.get('feeds')
            utils.log(data_list)
        else:
            data_list = [c]
        for data in data_list:
            s = classes.Series()
            layout = data.get('layout')
            if not layout:
                continue
            if layout.get('rowType') in ['policyChanges']:
                continue
            s.item_type = layout.get('itemType')
            s.feed_url = data.get('feedUrl')
            display = data.get('display')
            if display:
                if display.get('loggedIn'):
                    s.require_login = 'True'
            if sub_cat:
                if '[GENRE]' in s.feed_url:
                    s.feed_url = s.feed_url.replace('[GENRE]',
                                                    params.get('title'))
                if '[CHANNEL]' in s.feed_url:
                    s.feed_url = s.feed_url.replace('[CHANNEL]',
                                                    params.get('feed_id'))
            s.title = data.get('name')
            listing.append(s)
    for a in listing:
        utils.log(a.title)
    return listing


def create_program(entry):
    p = classes.Program()
    p.title = str(entry.get('name'))
    p.id = entry.get('id').split("/")[-1]
    p.thumbnail = entry.get('thumbnailUrl')
    p.description = entry.get('description')
    return p


def create_series(entry):
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.id = entry.get('id').split("/")[-1]
    s.feed_url = entry.get('feed')
    s.thumbnail = entry.get('thumbnailUrl')
    return s

def create_channel(entry):
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.feed_id = entry.get('feedId')
    s.thumbnail = entry.get('thumbnailUrl')
    return s

def create_genre_index(entry):
    utils.log('creating genre index item')
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.item_type = entry.get('type')
    s.thumbnail = entry.get('thumbnailUrl')
    return s


def get_entries(params):
    """
    Deal with everything else that isn't the main index! :)
    :param url:
    :return:
    """
    listing = []
    if params.get('require_login') == 'True':
        resp = fetch_protected_url(params.get('feed_url'))
    else:
        resp = fetch_url(params.get('feed_url'))
    json_data = json.loads(resp)
    for entry in json_data.get('itemListElement'):
        try:
            if params.get('item_type') == 'genre':
                p = create_genre_index(entry)
            elif entry.get('type') == 'TVSeries':
                p = create_series(entry)
            elif entry.get('type') == 'Channel':
                p = create_channel(entry)
                p.item_type = 'Channel'
            elif params.get('item_type') == 'hero':
                if entry.get('type') == 'Program':
                    p = create_series(entry.get('program'))
                elif entry.get('type') == 'VideoCarouselItem':
                    p = create_program(entry.get('video'))
            else:
                p = create_program(entry)
            listing.append(p)
        except Exception:
            utils.log('Error parsing entry')

    return listing


def get_stream(program_id):
    addon = xbmcaddon.Addon()
    token = get_login_token()
    if not token:
        return token
    data_url = config.STREAM_URL.format(
        VIDEOID=program_id,
        UNIQUEID=addon.getSetting('unique_id'),
        AAID=addon.getSetting('ad_id'),
        OPTOUT='true')
    video_stream_resp = fetch_protected_url(data_url, token)
    vs_data = json.loads(video_stream_resp)
    stream_info = {}
    for provider in vs_data.get('streamProviders'):
        if provider.get('providerName') == 'Akamai HLS':
            stream_info['stream_url'] = provider.get('contentUrl')
            subtitles = provider.get('subtitles')
            if subtitles:
                for subs in subtitles:
                    if subs.get('language') == 'en':
                        stream_info['subtitles'] = subs.get('srt')
                        break
    return stream_info