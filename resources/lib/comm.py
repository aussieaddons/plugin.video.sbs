#
#  SBS On Demand Kodi Add-on
#  Copyright (C) 2015 Andy Botting
#
#  This addon is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This addon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this addon. If not, see <http://www.gnu.org/licenses/>.
#

import base64
import classes
import config
import datetime
import json

from aussieaddonscommon import session
from aussieaddonscommon import utils

from bs4 import BeautifulSoup

try:
    import StorageServer
except ImportError:
    utils.log("script.common.plugin.cache not found!")
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer(utils.get_addon_id(), 1)


def fetch_url(url, headers=None):
    """Simple function that fetches a URL using requests."""
    with session.Session() as sess:
        if headers:
            sess.headers.update(headers)
        request = sess.get(url)
        try:
            request.raise_for_status()
        except Exception as e:
            # Just re-raise for now
            raise e
        data = request.text
    return data


def fetch_cache_url(url):
    """Call the get index function, but wrapped via caching"""
    return cache.cacheFunction(fetch_url, url)


def fetch_auth_token():
    """Perform a HTTP POST to secure server to fetch a token"""
    utils.log('Fetching new auth token')
    try:
        sess = session.Session()
        request = sess.post(config.token_url)
        request.raise_for_status()
        data = json.loads(request.text)
        token = data['sessiontoken']['response']['token']
        return token
    except Exception as e:
        raise Exception('Failed to fetch SBS streaming token: %s' % e)


def fetch_cache_token():
    """Get the token from cache is possible"""
    utils.log('Fetching cached token if possible')
    return cache.cacheFunction(fetch_auth_token)


def fetch_protected_url(url):
    """For protected URLs we add or Auth header when fetching"""
    token = fetch_cache_token()
    encoded_token = base64.encodestring('%s:android' % token).replace('\n', '')
    headers = {'Authorization': 'Basic ' + encoded_token}
    return fetch_url(url, headers)


def get_config():
    """This function fetches the SBS config"""
    try:
        resp = fetch_cache_url(config.config_url)
        sbs_config = json.loads(resp)
        return sbs_config
    except Exception:
        raise Exception("Error fetching SBS On Demand config."
                        "Service possibly unavailable")


def get_index():
    """Fetch the main index.

    This contains a mix of actual program information
    and URL references to other queries which return programs
    """
    resp = fetch_cache_url(config.index_url)
    json_data = json.loads(resp)
    return json_data['get']['response']['Menu']['children']


def get_category(category):
    """Fetch a given top level category from the index.

    This is usually programs and movies.
    """
    utils.log("Fetching category: %s" % category)
    index = get_index()
    for c in index:
        if c['name'] == category:
            return c


def get_section(category, section):
    utils.log("Fetching section: %s" % section)
    category = get_category(category)
    for s in category['children']:
        if s['name'] == section:
            return s


def get_series():
    series_list = []
    json_data = get_index()

    category_data = None
    for c in json_data['get']['response']['Menu']['children']:
        if c['name'] == 'Programs':
            category_data = c['children']
            break

    series_data = None
    for s in category_data:
        if s['name'] == 'Programs A-Z':
            series_data = s['children']
            break

    for entry in series_data:
        try:
            series = classes.Series()
            series.title = entry.get('name')
            series.id = entry.get('dealcodes')
            series.thumbnail = entry.get('thumbnail')
            series.num_episodes = int(entry.get('totalMpegOnly', 0))
            if series.num_episodes > 0:
                series_list.append(series)
        except Exception:
            utils.log('Error parsing entry: %s' % entry)
    return series_list


def get_categories(url):
    # TODO(andy): Switch to use this function
    resp = fetch_cache_url(url)
    json_data = json.loads(resp)

    series_list = []
    for entry in json_data['entries']:
        try:
            series = classes.Series()
            series.title = entry.get('name')
            series.id = entry.get('dealcodes')
            series.thumbnail = entry.get('thumbnail')
            series.num_episodes = int(entry.get('totalMpegOnly', 0))
            if series.num_episodes > 0:
                series_list.append(series)
        except Exception:
            utils.log('Error parsing entry: %s' % entry)
    return series_list


def create_program(jd):
    p = classes.Program()
    p.id = jd['id'].split('/')[-1]  # ID on the end of URL

    p.subfilename = jd.get('pl1$pilatId')

    p.title = jd.get('pl1$programName')
    if not p.title:
        p.title = jd.get('title')

    p.episode_title = jd.get('pl1$episodeTitle')
    try:
        p.series = int(jd.get('pl1$season'))
        p.episode = int(jd.get('pl1$episodeNumber'))
    except Exception:
        pass

    # If no other metadata available (mostly news), then use the
    # regular title, which probably includes the date
    if not p.series and not p.episode and not p.episode_title:
        p.title = jd.get('title')

    try:
        aired = int(jd.get('pubDate'))/1000
        p.date = datetime.datetime.fromtimestamp(aired)
    except Exception:
        pass

    try:
        expire = int(jd.get('media$expirationDate'))/1000
        p.expire = datetime.datetime.fromtimestamp(expire)
    except Exception:
        pass

    p.description = jd.get('pl1$shortSynopsis')
    if not p.description:
        p.description = jd.get('description')

    p.thumbnail = jd.get('thumbnail')
    if not p.thumbnail:
        for image in jd['media$thumbnails']:
            if 'Thumbnail Large' in image['plfile$assetTypes']:
                p.thumbnail = image['plfile$downloadUrl']
                break

    if 'media$content' in jd:
        # Sort media content by bitrate, highest last
        content_list = sorted(jd['media$content'],
                              key=lambda k: k['plfile$bitrate'])
        content = content_list[-1]

        try:
            p.duration = int(float(content.get('plfile$duration')))
        except Exception:
            utils.log("Failed to parse duration: %s" %
                      content.get('plfile$duration'))

        # Some shows, mostly clips aren't protected
        if 'Public' in content['plfile$assetTypes']:
            p.url = content['plfile$downloadUrl']
    else:
        utils.log("No 'media$content' found for %s" % p.title)

    return p


def get_entries(url):
    resp = fetch_cache_url(url)
    json_data = json.loads(resp)

    programs_list = []
    for entry in json_data['entries']:
        try:
            p = create_program(entry)
            programs_list.append(p)
        except Exception:
            utils.log('Error parsing entry')

    return programs_list


def get_stream(program_id):
    resp = fetch_protected_url(config.stream_url % program_id)
    xml = BeautifulSoup(resp, 'html.parser')
    stream = {}
    stream['url'] = xml.video['src']
    stream['subtitles'] = xml.find(
        'textstream', attrs={'type': 'text/srt'})['src']
    return stream
