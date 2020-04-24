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
        self.thumb = None
        self.fanart = None
        self.item_type = None
        self.feed_url = None
        self.title = None
        self.obj_type = 'Series'
        self.feed_id = None
        self.require_login = None
        self.multi_series = None
        self.single_series = None
        self.sub_category = None

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

    def get_thumb(self):
        return self.thumb

    def get_fanart(self):
        return self.fanart

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
        self.series_title = None
        self.episode_title = None
        self.description = None
        self.season_no = None
        self.episode_no = None
        self.category = None
        self.keywords = []
        self.rating = 'PG'
        self.duration = None
        self.date = None
        self.thumb = None
        self.fanart = None
        self.url = None
        self.expire = None
        self.subfilename = None
        self.obj_type = 'Program'

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.get_list_title(), other.get_list_title())

    def get_sort_title(self):
        sort_title = self.title.lower()
        sort_title = sort_title.replace('the ', '')
        return sort_title

    def get_title(self):
        return utils.descape(self.title)

    def get_episode_title(self):
        if self.episode_title:
            return utils.descape(self.episode_title)

    def get_series_title(self):
        return self.series_title

    #todo Fix only episode / only season
    def get_list_title(self):
        title = self.get_title()

        if (self.get_season_no() and self.get_episode_no()
                and self.get_series_title):
            # Series and episode information
            title = "{0} - S{1:02d}E{2:02d} - {3}".format(
                self.get_series_title(),
                self.get_season_no(),
                self.get_episode_no(),
                title)
        elif self.get_episode_no():
            # Only episode information
            title = "%s (E%02d)" % (title, self.get_episode_no())
        elif self.get_season_no():
            # Only season information
            title = "%s (S%02d)" % (title, self.get_season_no())

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

    def get_season_no(self):
        if self.season_no:
            return int(self.season_no)

    def get_episode_no(self):
        if self.episode_no:
            return int(self.episode_no)

    def get_thumb(self):
        if self.thumb:
            return utils.descape(self.thumb)

    def get_fanart(self):
        return self.fanart

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
        if self.get_season_no():
            info_dict['season'] = self.get_season_no()
        if self.get_episode_no():
            info_dict['episode'] = self.get_episode_no()
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


    def parse_kodi_url(self, url):
        params = dict(parse_qsl(url))
        for item in params.keys():
            setattr(self, item, unquote_plus(params[item]))
