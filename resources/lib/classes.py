import datetime
import re
import time
import unicodedata
from builtins import str
from collections import OrderedDict

from future.moves.urllib.parse import parse_qsl, quote_plus, unquote_plus

from aussieaddonscommon import utils


class Series(object):

    def __init__(self):
        self.description = None
        self.num_episodes = 0
        self.thumbnail = None
        self.item_type = None
        self.feed_url = None
        self.title = None
        self.obj_type = 'Series'
        self.feed_id = None
        self.require_login = None

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.get_sort_title(), other.get_sort_title())

    def get_sort_title(self):
        sort_title = self.title.lower()
        sort_title = sort_title.replace('the ', '')
        return sort_title

    def get_title(self):
        return utils.descape(self.title)

    def get_list_title(self):
        num_episodes = self.get_num_episodes()
        if num_episodes:
            return "{0} ({1})".format(self.get_title(), num_episodes)
        else:
            return self.get_title()

    def get_season(self):
        season = re.search('^.* Series (?P<season>\d+)$', self.get_title())
        if season is None:
            return 0
        return int(season.group('season'))

    def increment_num_episodes(self):
        self.num_episodes += 1

    def get_num_episodes(self):
        return self.num_episodes

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail

    def get_description(self):
        if self.description:
            return self.description

    def make_kodi_url(self):
        d_original = OrderedDict(
            sorted(self.__dict__.items(), key=lambda x: x[0]))
        d = d_original.copy()
        for key, value in d_original.items():
            if not value:
                d.pop(key)
                continue
            if isinstance(value, str):
                d[key] = unicodedata.normalize(
                    'NFKD', value).encode('ascii', 'ignore').decode('utf-8')
        url = ''
        for key in d.keys():
            if isinstance(d[key], (str, bytes)):
                val = quote_plus(d[key])
            else:
                val = d[key]
            url += '&{0}={1}'.format(key, val)
        return url

    def parse_kodi_url(self, url):
        params = dict(parse_qsl(url))
        for item in params.keys():
            setattr(self, item, unquote_plus(params[item]))
        if self.date:
            try:
                self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
            except TypeError:
                self.date = datetime.datetime(
                    *(time.strptime(self.date, "%Y-%m-%d")[0:6]))


class Program(object):

    def __init__(self):
        self.id = -1
        self.title = None
        self.episode_title = None
        self.description = None
        self.series = None
        self.episode = None
        self.category = None
        self.keywords = []
        self.rating = 'PG'
        self.duration = None
        self.date = None
        self.thumbnail = None
        self.url = None
        self.expire = None
        self.subfilename = None
        self.obj_type = 'Program'

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return (cmp(self.title, other.title) or
                cmp(self.series, other.series) or
                cmp(self.episode, other.episode))

    def get_sort_title(self):
        sort_title = self.title.lower()
        sort_title = sort_title.replace('the ', '')
        return sort_title

    def get_title(self):
        return utils.descape(self.title)

    def get_episode_title(self):
        if self.episode_title:
            return utils.descape(self.episode_title)

    def get_list_title(self):
        title = self.get_title()

        if (self.get_season() and self.get_episode()):
            # Series and episode information
            title = "%s (S%02dE%02d)" % (title, self.get_season(),
                                         self.get_episode())
        elif self.get_episode():
            # Only episode information
            title = "%s (E%02d)" % (title, self.get_episode())
        elif self.get_season():
            # Only season information
            title = "%s (S%02d)" % (title, self.get_season())

        if self.get_episode_title():
            title = "%s: %s" % (title, self.get_episode_title())

        return title

    def get_description(self):
        description = ""
        if self.description:
            description = self.description
        if self.expire:
            expire = "Expires: %s" % self.expire.strftime('%a, %d %b %Y')
            description = "%s\n%s" % (description, expire)
        return utils.descape(description)

    def get_category(self):
        if self.category:
            return utils.descape(self.category)

    def get_rating(self):
        if self.rating:
            return utils.descape(self.rating)

    def get_duration(self):
        if self.duration:
            version = utils.get_kodi_major_version()
            seconds = int(self.duration)
            if version < 15:
                # Older versions use minutes
                minutes = seconds / 60
                return minutes
            else:
                # Kodi v15 uses seconds
                return seconds

    def get_date(self):
        if self.date:
            return self.date.strftime("%Y-%m-%d")

    def get_year(self):
        if self.date:
            return self.date.year

    def get_season(self):
        if self.series:
            return int(self.series)

    def get_episode(self):
        if self.episode:
            return int(self.episode)

    def get_thumbnail(self):
        if self.thumbnail:
            return utils.descape(self.thumbnail)

    def get_url(self):
        if self.url:
            return utils.descape(self.url)

    def get_expire(self):
        if self.expire:
            return self.expire.strftime("%Y-%m-%d %h:%m:%s")

    def get_subfilename(self):
        if self.subfilename:
            return self.subfilename+'.SRT'

    def get_kodi_list_item(self):
        info_dict = {}
        if self.get_title():
            info_dict['tvshowtitle'] = self.get_title()
        if self.get_episode_title():
            info_dict['title'] = self.get_episode_title()
        if self.get_category():
            info_dict['genre'] = self.get_category()
        if self.get_description():
            info_dict['plot'] = self.get_description()
        if self.get_description():
            info_dict['plotoutline'] = self.get_description()
        if self.get_duration():
            info_dict['duration'] = self.get_duration()
        if self.get_year():
            info_dict['year'] = self.get_year()
        if self.get_date():
            info_dict['aired'] = self.get_date()
        if self.get_season():
            info_dict['season'] = self.get_season()
        if self.get_episode():
            info_dict['episode'] = self.get_episode()
        if self.get_rating():
            info_dict['mpaa'] = self.get_rating()
        return info_dict

    def get_kodi_audio_stream_info(self):
        info_dict = {}
        # This information may be incorrect
        info_dict['codec'] = 'aac'
        info_dict['language'] = 'en'
        info_dict['channels'] = 2
        return info_dict

    def get_kodi_video_stream_info(self):
        info_dict = {}
        if self.get_duration():
            info_dict['duration'] = self.get_duration()

        # This information may be incorrect
        info_dict['codec'] = 'h264'
        info_dict['width'] = '640'
        info_dict['height'] = '360'
        return info_dict

    def make_kodi_url(self):
        d_original = OrderedDict(
            sorted(self.__dict__.items(), key=lambda x: x[0]))
        d = d_original.copy()
        for key, value in d_original.items():
            if not value:
                d.pop(key)
                continue
            if isinstance(value, str):
                d[key] = unicodedata.normalize(
                    'NFKD', value).encode('ascii', 'ignore').decode('utf-8')
        url = ''
        for key in d.keys():
            if isinstance(d[key], (str, bytes)):
                val = quote_plus(d[key])
            else:
                val = d[key]
            url += '&{0}={1}'.format(key, val)
        return url

    def make_xbmc_url(self):
        d = {}
        if self.id:
            d['id'] = self.id
        if self.title:
            d['title'] = self.title
        if self.episode_title:
            d['episode_title'] = self.episode_title
        if self.description:
            d['description'] = self.description
        if self.duration:
            d['duration'] = self.duration
        if self.category:
            d['category'] = self.category
        if self.rating:
            d['rating'] = self.rating
        if self.date:
            d['date'] = self.date.strftime("%Y-%m-%d %H:%M:%S")
        if self.thumbnail:
            d['thumbnail'] = self.thumbnail
        if self.url:
            d['url'] = self.url
        if self.subfilename:
            d['subfilename'] = self.subfilename

        return utils.make_url(d)

    def parse_xbmc_url(self, string):
        d = utils.get_url(string)
        self.id = d.get('id')
        self.title = d.get('title')
        self.episode_title = d.get('episode_title')
        self.description = d.get('description')
        self.duration = d.get('duration')
        self.category = d.get('category')
        self.rating = d.get('rating')
        self.url = d.get('url')
        self.thumbnail = d.get('thumbnail')
        self.subfilename = d.get('subfilename')
        if 'date' in d:
            timestamp = time.mktime(time.strptime(d['date'],
                                                  '%Y-%m-%d %H:%M:%S'))
            self.date = datetime.date.fromtimestamp(timestamp)
