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


def get_attr(attrs, key, val, result_key='', default=None):
    for attr in attrs:
        if attr.get(key) == val:
            if result_key:
                return attr.get(result_key)
            else:
                return attr
    return default


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
        else:
            data_list = [c]
        for data in data_list:
            title = data.get('name')
            if (title == 'Football Highlights' and
                    params.get('title') != 'Sport'):
                continue
            s = classes.Series()
            s.title = title
            layout = data.get('layout')
            if not layout:
                continue
            if layout.get('rowType') in ['policyChanges']:
                continue
            s.item_type = layout.get('itemType')
            s.feed_url = data.get('feedUrl')
            if s.item_type in ['genre']:
                s.feed_url += '&range=1-100'
            display = data.get('display')
            if display:
                if display.get('loggedIn'):
                    s.require_login = 'True'
            if sub_cat:
                s.sub_category = 'True'
                if '[GENRE]' in s.feed_url:
                    s.feed_url = s.feed_url.replace('[GENRE]',
                                                    params.get('title'))
                if '[CHANNEL]' in s.feed_url:
                    s.feed_url = s.feed_url.replace('[CHANNEL]',
                                                    params.get('feed_id'))

            listing.append(s)
    for a in listing:
        utils.log(a.title)
    return listing


def create_program(entry):
    p = classes.Program()
    p.id = entry.get('id').split("/")[-1]
    p.thumb = entry.get('thumbnailUrl')
    p.description = entry.get('description')
    p.season_no = entry.get('partOfSeason', {}).get('seasonNumber')
    p.episode_no = entry.get('episodeNumber')
    titles = entry.get('displayTitles')
    if titles and p.season_no and p.episode_no:
        p.series_title = titles.get('title')
        p.title = titles.get('videoPlayer', {}).get('title')
        if not p.series_title or not p.title:
            p.title = entry.get('name')
            p.series_title = None
    else:
        p.title = entry.get('name')
    return p


def create_series(entry):
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.id = entry.get('id').split("/")[-1]
    s.thumb = entry.get('thumbnailUrl')
    seasons = entry.get('containSeasons', [])
    if len(seasons) > 1:
        s.multi_series = 'True'
    else:
        s.single_series = 'True'
    s.feed_url = config.SERIES_URL.replace('[SERIESID]', s.id)
    return s

def create_channel(entry):
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.feed_id = entry.get('feedId')
    s.thumb = entry.get('thumbnailUrl')
    return s

def create_genre_index(entry):
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.item_type = entry.get('type')
    s.thumb = entry.get('thumbnailUrl')
    return s


def create_season(entry, thumb):
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.thumb = thumb
    s.feed_url = entry.get('feedUrl')
    return s


def create_collection(entry):
    s = classes.Series()
    s.title = str(entry.get('name'))
    s.description = entry.get('description')
    s.feed_url = entry.get('feedUrl')
    s.item_type = entry.get('type')
    thumbs = entry.get('thumbnails', [])
    s.fanart = get_attr(thumbs, 'name', 'Background 2X', 'contentUrl')
    s.thumb = get_attr(thumbs, 'name', 'Thumbnail Large', 'contentUrl')
    return s


def create_seasons_list(seasons, thumb):
    listing = []
    for entry in seasons.get('feeds'):
        try:
            s = create_season(entry, thumb)
            listing.append(s)
        except Exception:
            utils.log('Error parsing season entry')
    return listing


def get_entries(params):
    """
    Deal with everything else that isn't the main index or a category/genre! :)
    :param url:
    :return:
    """
    listing = []
    sort = False
    multi_page = False
    feed_url = params.get('feed_url')
    if params.get('item_type') == 'Collection':
        feed_url += '&range=1-100'
        multi_page = True
        sort = True
    elif params.get('sub_category') == 'True':
        if params.get('title') == 'All Programs A-Z':
            feed_url += '&range=1-100'
            multi_page = True
        else:
            feed_url += '&range=1-50'
    if params.get('require_login') == 'True':
        token = get_login_token()
        resp = fetch_protected_url(feed_url, token)
    else:
        resp = fetch_url(feed_url)
    json_data = json.loads(resp)
    if params.get('multi_series') == 'True':
        thumb = json_data.get('program').get('thumbnailUrl')
        seasons = get_attr(
            json_data.get('rows'), 'name', 'Seasons', default=[])
        for season in create_seasons_list(seasons, thumb):
            listing.append(season)
    else:
        if params.get('single_series') == 'True':  # flatten single series
            seasons = get_attr(
                json_data.get('rows'), 'name', 'Seasons', 'feeds', default=[])
            season = seasons[0]
            json_data = json.loads(fetch_url(season.get('feedUrl')))
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
                elif params.get('item_type') == 'collection':
                    p = create_collection(entry)
                else:
                    p = create_program(entry)
                listing.append(p)
            except Exception:
                raise  # remove once stable
                utils.log('Error parsing entry')
    if sort:
        listing = sorted(listing)
    if multi_page:
        pass
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