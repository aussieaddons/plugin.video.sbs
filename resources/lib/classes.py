import datetime
import re
import time
import unicodedata
from builtins import str
from collections import OrderedDict
from functools import total_ordering

from future.moves.urllib.parse import parse_qsl, quote_plus, unquote_plus

from aussieaddonscommon import utils


def comp(x, y):
    return (x > y) - (x < y)


@total_ordering
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
        self.entry_type = None
        self.feed_id = None
        self.require_login = None
        self.multi_series = None
        self.single_series = None
        self.category = None
        self.sub_category = None
        self.rating = None
        self.country = None
        self.page_begin = None
        self.page_size = None
        self.id = None
        self.favourite = None

    def __repr__(self):
        return self.title

    def __lt__(self, other):
        return comp(self.get_sort_title(), other.get_sort_title()) < 0

    def __eq__(self, other):
        return comp(self.get_sort_title(), other.get_sort_title()) == 0

    def get_sort_title(self):
        sort_title = self.title.lower()
        sort_title = sort_title.replace('the ', '')
        return sort_title

    def get_title(self):
        return self.title

    def get_list_title(self):
        num_episodes = self.get_num_episodes()
        if num_episodes:
            return "{0} ({1})".format(self.get_title(), num_episodes)
        else:
            return self.get_title()

    def get_season(self):
        season = re.search('^.* Series (?P<season>\\d+)$', self.get_title())
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

    def get_category(self):
        return self.category

    def get_sub_category(self):
        return self.sub_category

    def get_country(self):
        return self.country

    def get_rating(self):
        return self.rating

    def get_description(self):
        return self.description

    def get_extended_description(self):
        description = ''
        if self.category:
            description += 'Genre: %s\n' % self.get_category()
        if self.sub_category:
            description += 'Collection: %s\n' % self.get_sub_category()
        if self.country:
            description += 'Country: %s\n' % self.get_country()
        if self.rating:
            description += 'Rated: %s\n' % self.get_rating()
        if self.description:
            if description:
                description += '\n'
            description += self.get_description()
        return description

    def get_kodi_list_item(self):
        info_dict = {}
        if self.get_title():
            info_dict['tvshowtitle'] = self.get_title()
        if self.get_category():
            info_dict['genre'] = self.get_category()
        if self.get_sub_category():
            info_dict['tag'] = self.get_sub_category()
        if self.get_extended_description():
            info_dict['plot'] = self.get_extended_description()
        if self.get_description():
            info_dict['plotoutline'] = self.get_description()
        if self.get_rating():
            info_dict['mpaa'] = self.get_rating()
        if self.get_country():
            info_dict['country'] = self.get_country()
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
        url += '&addon_version={0}'.format(utils.get_addon_version())
        return url

    def parse_kodi_url(self, url):
        params = dict(parse_qsl(url))
        params.pop('addon_version', '')
        for item in params.keys():
            setattr(self, item, unquote_plus(params[item]))
        if self.date:
            try:
                self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
            except TypeError:
                self.date = datetime.datetime(
                    *(time.strptime(self.date, "%Y-%m-%d")[0:6]))


@total_ordering
class Program(object):

    def __init__(self):
        self.id = None
        self.title = None
        self.series_title = None
        self.description = None
        self.season_no = None
        self.episode_no = None
        self.category = None
        self.keywords = []
        self.rating = None
        self.duration = None
        self.creditsBegin = None
        self.date = None
        self.thumb = None
        self.fanart = None
        self.url = None
        self.expire = None
        self.subfilename = None
        self.obj_type = 'Program'
        self.entry_type = None
        self.favourite = False
        self.pilatDealcode = None
        self.needs_ia = False

    def __repr__(self):
        return self.title

    def __lt__(self, other):
        return comp(self.get_sort_title(), other.get_sort_title()) < 0

    def __eq__(self, other):
        return comp(self.get_sort_title(), other.get_sort_title()) == 0

    def get_sort_title(self):
        sort_title = self.title.lower()
        sort_title = sort_title.replace('the ', '')
        return sort_title

    def get_title(self):
        return self.title

    def get_series_title(self):
        return self.series_title

    def get_list_title(self):
        season = self.get_season_no()
        season = 'S{0:02d}'.format(season) if season else ''
        episode = self.get_episode_no()
        episode = 'E{0:02d}'.format(episode) if episode else ''
        season_episode = '{0}{1}'.format(season, episode)

        series = self.get_series_title()
        title = self.get_title()
        if not series:
            series = title
            title = ''

        return ' - '.join(filter(None, (series, season_episode, title)))

    def get_description(self):
        description = ""
        if self.description:
            description = self.description
        if self.expire:
            expire = self.get_expire(True).strftime('%a, %d %b %Y')
            description = "%s\n\nExpires: %s" % (description, expire)
        return description

    def get_category(self):
        if self.category:
            return self.category

    def get_rating(self):
        return self.rating

    def get_duration(self):
        if self.duration:
            version = utils.get_kodi_major_version()
            seconds = int(float(self.duration))
            if version < 15:
                # Older versions use minutes
                minutes = seconds // 60
                return minutes
            else:
                # Kodi v15 uses seconds
                return seconds

    def get_credits_time(self):
        if self.creditsBegin:
            return int(self.creditsBegin)

    dt_format = '%Y-%m-%dT%H:%M:%SZ'

    @staticmethod
    def parse_date(dt_str):
        try:
            date = datetime.datetime.strptime(dt_str, Program.dt_format)
        except TypeError:
            date = datetime.datetime(
                *(time.strptime(dt_str, Program.dt_format)[0:6]))

        return date

    @staticmethod
    def format_date(dt_obj):
        return dt_obj.strftime(Program.dt_format)

    def get_date(self, as_datetime=False):
        if not self.date:
            return None
        if not isinstance(self.date, datetime.datetime):
            self.date = Program.parse_date(self.date)

        return self.date if as_datetime else self.date.strftime("%Y-%m-%d")

    def get_year(self):
        if self.date:
            return self.get_date(True).year

    def get_tvshowid(self):
        return self.pilatDealcode

    def get_season_no(self):
        if self.season_no:
            try:
                return int(self.season_no)
            except ValueError:
                if isinstance(self.season_no, float):
                    utils.log(
                        'Invalid season number (float {0}), rounding to '
                        'int'.format(
                            self.season_no))
                    return int(float(self.season_no))
                else:
                    utils.log(
                        'Invalid season number (string {0}), returning '
                        '0'.format(
                            self.season_no))
                    return 0

    def get_episode_no(self):
        if self.episode_no:
            try:
                return int(self.episode_no)
            except ValueError:
                if isinstance(self.episode_no, float):
                    utils.log(
                        'Invalid episode number (float {0}), rounding to '
                        'int'.format(
                            self.episode_no))
                    return int(float(self.episode_no))
                else:
                    utils.log(
                        'Invalid episode number (string {0}), returning '
                        '0'.format(
                            self.episode_no))
                    return 0

    def get_thumb(self):
        return self.thumb

    def get_fanart(self):
        return self.fanart

    def get_url(self):
        return self.url

    def get_expire(self, as_datetime=False):
        if not isinstance(self.expire, datetime.datetime):
            self.expire = Program.parse_date(self.expire)

        if as_datetime:
            return self.expire
        else:
            return self.expire.strftime("%Y-%m-%d %H:%M:%S")

    def get_subfilename(self):
        if self.subfilename:
            return self.subfilename + '.SRT'

    def get_kodi_list_item(self):
        info_dict = {}
        if self.get_series_title():
            info_dict['tvshowtitle'] = self.get_series_title()
        if self.get_title():
            info_dict['title'] = self.get_list_title()
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
        info_dict['mediatype'] = 'episode'
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
            elif isinstance(d[key], datetime.datetime):
                val = quote_plus(Program.format_date(d[key]))
            else:
                val = d[key]
            url += '&{0}={1}'.format(key, val)
        url += '&addon_version={0}'.format(utils.get_addon_version())
        return url.lstrip('&')

    def parse_kodi_url(self, url):
        url = url.lstrip('?')
        params = dict(parse_qsl(url))
        params.pop('addon_version', '')
        for item in params.keys():
            setattr(self, item, unquote_plus(params[item]))
