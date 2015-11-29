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

import urllib2
import config
import classes
import json
import utils
import gzip
from BeautifulSoup import BeautifulStoneSoup

try:
    import StorageServer
except:
    utils.log("script.common.plugin.cache not found!")
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer(config.ADDON_ID, 1)


class JsonRedirectHandler(urllib2.HTTPRedirectHandler): 
    def http_error_301(self, req, fp, code, msg, headers):
        utils.log('Redirected to: %s' % headers['location'])
        headers['location'] += '.json'
        return urllib2.HTTPRedirectHandler.http_error_301(self, req, fp,
                                                          code, msg, headers)

def fetch_url(url, headers={}):
    """ Fetches a URL using urllib2 with some basic retry.
        An exception is raised if an error (e.g. 404) occurs after the max
        number of retries.
    """
    utils.log("Fetching URL: %s" % url)
    request = urllib2.Request(url, None, dict(headers.items() + {
        'User-Agent' : config.user_agent
    }.items()))

    attempts = 10
    attempt = 0
    fail_exception = Exception("Unknown failure in URL fetch")

    while attempt < attempts:
        try:
            # Should always return < 10s, if not, it's a fail
            timeout = 10
            http = urllib2.urlopen(request, timeout=timeout)
            return http.read()
        except Exception, e:
            fail_exception = e
            attempt += 1
            utils.log('Error fetching URL: "%s". Attempting to retry %d/%d'
                      % (e, attempt, attempts))

    # Pass the last exception though
    raise fail_exception

def fetch_protected_url(url):
    """ For protected URLs we add or Auth header when fetching
    """
    headers = {'Authorization': 'Basic ' + config.auth_string}
    return fetch_url(url, headers)

def get_config():
    """This function fetches the iView "config". Among other things,
        it tells us an always-metered "fallback" RTMP server, and points
        us to many of iView's other XML files.
    """
    try:
        resp = fetch_url(config.config_url)
        sbs_config = json.loads(resp)
        return sbs_config
    except:
        raise Exception("Error fetching SBS On Demand config."
                        "Service possibly unavailable")

def get_index_base():
    """ Fetch the main index. This contains a mix of actual program information
        and URL references to other queries which return programs
    """
    resp = fetch_url(config.index_url)
    json_data = json.loads(resp)
    return json_data['get']['response']['Menu']['children']

def get_index():
    """ Call the get index function, but wrapped via caching
    """
    return cache.cacheFunction(get_index_base)

def get_category(category):
    """ Fetch a given top level category from the index. This is usually
        programs and movies.
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
        except:
            utils.log('Error parsing entry: %s' % entry)
    return series_list

def get_categories(url):
    # TODO: Switch to use this function
    resp = fetch_url(url)
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
        except:
            utils.log('Error parsing entry: %s' % entry)
    return series_list

def get_entries(url):
    resp = fetch_url(url)
    json_data = json.loads(resp)

    programs_list = []
    for entry in json_data['entries']:
        try:
            p = classes.Program()
            p.id = entry['id'].split('/')[-1] # ID on the end of URL

            p.title = entry.get('pl1$programName')
            if not p.title:
                # We ignore anything without pl1$programName as they're usually
                # web clips
                break

            p.episode_title = entry.get('pl1$episodeTitle')
            p.series = entry.get('pl1$season')
            p.episode = entry.get('pl1$episodeNumber')
            p.description = entry.get('pl1$shortSynopsis')
            p.duration = entry['media$content'][-1]['plfile$duration']
            #TODO: p.aired
   
            for image in entry['media$thumbnails']:
                if 'Thumbnail Large' in image['plfile$assetTypes']:
                    p.thumbnail = image['plfile$downloadUrl']
                    break

            # Sort media content by bitrate, highest last
            content_list = sorted(entry['media$content'],
                                  key=lambda k: k['plfile$bitrate'])
            content = content_list[-1]

            # Some shows, mostly clips aren't protected
            p.duration = content['plfile$duration']
            if 'Public' in content['plfile$assetTypes']:
                p.url = content['plfile$downloadUrl']

            programs_list.append(p)
        except:
            utils.log('Error parsing entry')

    return programs_list

def get_stream(program_id):
    resp = fetch_protected_url(config.stream_url % program_id)
    xml = BeautifulStoneSoup(resp)
    for entry in xml.findAll('video', src=True):
       # We get multiples of the same URL, so just use the first
       return entry['src']

