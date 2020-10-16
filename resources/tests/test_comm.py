from __future__ import absolute_import, unicode_literals

import io
import json
import os
import re

try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.comm as comm
import resources.lib.config as config
from resources.tests.fakes import fakes


class CommTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/auth1.json'), 'rb') as f:
            self.AUTH1_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/auth1_fail.json'), 'rb') as f:
            self.AUTH1_FAIL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/auth2.json'), 'rb') as f:
            self.AUTH2_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/feed_popular.json'),
                  'rb') as f:
            self.FEED_POPULAR_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/genre_factual_latest.json'),
                  'rb') as f:
            self.GENRE_FACTUAL_LATEST_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/hero.json'), 'rb') as f:
            self.HERO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_channels.json'),
                  'rb') as f:
            self.VIDEO_CHANNELS_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_collections.json'),
                  'rb') as f:
            self.VIDEO_COLLECTIONS_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_config.json'),
                  'rb') as f:
            self.VIDEO_CONFIG_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_add.json'),
                  'rb') as f:
            self.VIDEO_FAVOURITE_ADD_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_all.json'),
                  'rb') as f:
            self.VIDEO_FAV_ALL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_remove.json'),
                  'rb') as f:
            self.VIDEO_FAVOURITE_REMOVE_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_feed.json'), 'rb') as f:
            self.VIDEO_FEED_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_genres.json'),
                  'rb') as f:
            self.VIDEO_GENRES_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/json/video_program_collection.json'),
                'rb') as f:
            self.VIDEO_PROGRAM_COLLECTION_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_program_series.json'),
                  'rb') as f:
            self.VIDEO_PROGRAM_SERIES_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_search_movies.json'),
                  'rb') as f:
            self.VIDEO_SEARCH_MOVIES_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_search_upnext.json'),
                  'rb') as f:
            self.VIDEO_SEARCH_UPNEXT_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_stream.json'),
                  'rb') as f:
            self.VIDEO_STREAM_JSON = io.BytesIO(f.read()).read()
        self.CONFIG = json.loads(self.VIDEO_CONFIG_JSON)

    @responses.activate
    def test_get_entries_hero(self):
        responses.add(responses.GET, 'https://foo.bar/hero&range=1-50',
                      body=self.HERO_JSON,
                      status=200)
        params = {'item_type': 'hero', 'obj_type': 'Series',
                  'feed_url': 'https://foo.bar/hero', 'title': 'Hero carousel'}
        observed = comm.get_entries(params)
        self.assertEqual(9, len(observed))
        self.assertEqual('362510403921', observed[8].id)

    @mock.patch('resources.lib.comm.get_login_token')
    @responses.activate
    def test_get_favourites_categories(self, mock_token):
        mock_token.return_value = 'foo'
        conf = json.loads(self.VIDEO_CONFIG_JSON)
        fav_all_url = conf.get('favourites').get('listAll')
        responses.add(responses.GET, fav_all_url,
                      body=self.VIDEO_FAV_ALL_JSON,
                      status=200)
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        listing = comm.get_favourites_categories()
        self.assertEqual(1, len(listing))
        self.assertEqual('Programs', listing[0].get_title())

    @mock.patch('xbmcgui.Dialog.input')
    @mock.patch('uuid.uuid4')
    @mock.patch('xbmcaddon.Addon', fakes.FakeAddon)
    @responses.activate
    def test_get_login_token(self, mock_uuid, mock_input):
        mock_uuid.side_effect = fakes.UUID
        mock_input.side_effect = fakes.LOGIN
        responses.add(responses.POST, config.LOGIN1_URL,
                      body=self.AUTH1_JSON,
                      status=200)
        responses.add(responses.GET,
                      config.LOGIN2_URL.format(token=json.loads(
                          self.AUTH1_JSON).get('access_token')),
                      body=self.AUTH2_JSON,
                      status=200)
        observed = comm.get_login_token()
        self.assertEqual(fakes.LOGIN_TOKEN, observed)

    @responses.activate
    def test_get_category_programs(self):
        params = {'category': 'Programs'}
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        observed = comm.get_category(params)
        self.assertEqual(18, len(observed))
        self.assertEqual('Genres', observed[0].get_title())

    @responses.activate
    def test_get_category_film_genre(self):
        params = {'item_type': 'FilmGenre',
                  'obj_type': 'Series',
                  'thumb': 'https://foo.bar/drama.jpg',
                  'title': 'Drama'}
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        observed = comm.get_category(params)
        self.assertEqual(3, len(observed))
        self.assertEqual('Recently Added', observed[0].get_title())
        self.assertIn('Drama', observed[0].feed_url)

    @responses.activate
    def test_get_category_channel(self):
        params = {'item_type': 'Channel',
                  'obj_type': 'Series',
                  'feed_id': 'SBS2',
                  'title': 'SBS VICELAND'}
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        observed = comm.get_category(params)
        self.assertEqual(3, len(observed))
        self.assertEqual('From Last Night', observed[0].get_title())
        self.assertIn('SBS2', observed[0].feed_url)

    def test_create_program(self):
        program = json.loads(self.VIDEO_FEED_JSON).get('itemListElement')[0]
        observed = comm.create_program(program)
        self.assertEqual('New Girl - S02E01 - Re-Launch',
                         observed.get_list_title())

    def test_create_series(self):
        series = json.loads(self.FEED_POPULAR_JSON).get('itemListElement')[0]
        observed = comm.create_series(series)
        self.assertEqual('Brooklyn Nine-Nine', observed.get_list_title())

    def test_create_channel(self):
        channel = json.loads(
            self.VIDEO_CHANNELS_JSON).get('itemListElement')[0]
        observed = comm.create_channel(channel)
        self.assertEqual('SBS', observed.get_list_title())

    def test_create_genre_index(self):
        genre = json.loads(self.VIDEO_GENRES_JSON).get('itemListElement')[0]
        observed = comm.create_genre_index(genre)
        self.assertEqual('Factual', observed.get_list_title())

    def test_create_season(self):
        season = json.loads(
            self.VIDEO_PROGRAM_SERIES_JSON)['rows'][1]['feeds'][0]
        observed = comm.create_season(season, '')
        self.assertIn('181023', observed.feed_url)

    def test_create_collection(self):
        collection = json.loads(
            self.VIDEO_COLLECTIONS_JSON).get('itemListElement')[0]
        observed = comm.create_collection(collection)
        self.assertEqual('Adored Adaptations', observed.get_list_title())

    def test_create_seasons_list(self):
        seasons = json.loads(self.VIDEO_PROGRAM_SERIES_JSON)['rows'][1]
        observed = comm.create_seasons_list(seasons, '')
        self.assertEqual(2, len(observed))

    @responses.activate
    def test_create_search(self):
        search = self.CONFIG.get(
            'contentStructure')['screens']['Search']['tabs'][0]['rows'][2]
        responses.add(responses.GET,
                      search.get('feedUrl').replace('[QUERY]', 'news'),
                      body=self.VIDEO_SEARCH_MOVIES_JSON,
                      status=200)
        observed = comm.create_search(search, 'news')
        self.assertEqual(3, observed.get_num_episodes())

    def test_append_range(self):
        url = 'https://foo.bar/items?q=1'
        begin = 101
        size = 50
        observed = comm.append_range(url, begin, size)
        self.assertEqual('https://foo.bar/items?q=1&range=101-150', observed)

    def test_create_page(self):
        feed_url = 'https://foo.bar/items?q=1'
        begin = 51
        size = 50
        observed = comm.create_page(begin, size, feed_url)
        self.assertEqual('Next page (51 - 100)', observed.get_list_title())

    def test_create_fav_category(self):
        title = 'foobar'
        feed_url = 'https://foo.bar/items?q=1'
        observed = comm.create_fav_category(title, feed_url)
        self.assertEqual(True, observed.favourite)

    @responses.activate
    def test_get_search_results(self):
        params = {'action': 'searchhistory', 'name': 'news'}
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        for tab in self.CONFIG.get(
                'contentStructure')['screens']['Search']['tabs']:
            for cat in tab.get('rows'):
                responses.add(responses.GET,
                              cat.get('feedUrl').replace('[QUERY]', 'news'),
                              body=self.VIDEO_SEARCH_MOVIES_JSON,
                              status=200)
        observed = comm.get_search_results(params)
        self.assertEqual(5, len(observed))
        self.assertEqual('Episodes (3)', observed[4].get_list_title())

    @responses.activate
    def test_get_entries_programs(self):
        feed_url = 'https://foo.bar/items?q=1'
        params = {'item_type': 'title-under', 'obj_type': 'Series',
                  'sub_category': 'True',
                  'feed_url': feed_url,
                  'title': 'Latest Content'}
        responses.add(responses.GET, '{0}{1}'.format(feed_url, '&range=1-50'),
                      body=self.VIDEO_FEED_JSON,
                      status=200)
        observed = comm.get_entries(params)
        self.assertEqual(18, len(observed))
        self.assertEqual(8, observed[7].get_episode_no())

    @responses.activate
    def test_get_entries_collections(self):
        feed_url = 'https://foo.bar/items?q=1'
        params = {'item_type': 'title-under', 'obj_type': 'Series',
                  'feed_url': feed_url,
                  'title': 'Best Of International Crime '}
        responses.add(responses.GET, '{0}{1}'.format(feed_url, '&range=1-50'),
                      body=self.VIDEO_PROGRAM_COLLECTION_JSON,
                      status=200)
        observed = comm.get_entries(params)
        self.assertEqual(27, len(observed))

    @responses.activate
    def test_get_next_program(self):
        data = json.loads(self.VIDEO_FEED_JSON).get('itemListElement')[0]
        program = comm.create_program(data)

        url = re.compile('^https://www.sbs.com.au/api/v3/video_search/')
        responses.add(responses.GET, url,
                      body=self.VIDEO_SEARCH_UPNEXT_JSON,
                      status=200)
        observed = comm.get_next_program(program)
        self.assertEqual(2, observed.get_episode_no())

    @mock.patch('resources.lib.comm.get_login_token')
    @responses.activate
    def test_get_favourites_data(self, mock_token):
        mock_token.return_value = 'foo'
        fav_url = self.CONFIG.get('favourites').get('listAll')
        responses.add(responses.GET, fav_url,
                      body=self.VIDEO_FAV_ALL_JSON,
                      status=200)
        observed = comm.get_favourites_data(self.CONFIG)
        self.assertEqual(True, observed.get('all').get('status'))

    @mock.patch('resources.lib.comm.get_login_token')
    def test_get_favourites_data_no_token(self, mock_token):
        mock_token.return_value = False
        observed = comm.get_favourites_data(self.CONFIG)
        self.assertEqual({}, observed)

    @mock.patch('resources.lib.comm.get_config')
    @mock.patch('resources.lib.comm.get_favourites_data')
    def test_get_favourties_categories(self, mock_fav_data, mock_config):
        mock_config.return_value = self.CONFIG
        mock_fav_data.return_value = json.loads(self.VIDEO_FAV_ALL_JSON)
        observed = comm.get_favourites_categories()
        self.assertEqual(1, len(observed))
        self.assertEqual('Programs', observed[0].get_list_title())

    @mock.patch('resources.lib.comm.get_config')
    @mock.patch('resources.lib.comm.get_login_token')
    @responses.activate
    def test_add_to_favourites(self, mock_token, mock_config):
        mock_token.return_value = 'foo'
        mock_config.return_value = self.CONFIG
        url = re.compile('^https://www.sbs.com.au/api/v3/video_favourite/add')
        params = {'action': 'addfavourites', 'entry_type': 'TVSeries',
                  'program_id': '6000'}
        responses.add(responses.GET, url,
                      body=self.VIDEO_FAVOURITE_ADD_JSON,
                      status=200)
        observed = comm.add_to_favourites(params)
        self.assertIs(True, observed)

    @mock.patch('resources.lib.comm.get_login_token')
    def test_add_to_favourites_no_token(self, mock_token):
        mock_token.return_value = False
        params = {'action': 'addfavourites', 'entry_type': 'TVSeries',
                  'program_id': '6000'}
        observed = comm.add_to_favourites(params)
        self.assertIs(None, observed)

    @mock.patch('resources.lib.comm.get_config')
    @mock.patch('resources.lib.comm.get_login_token')
    @responses.activate
    def test_remove_from_favourites(self, mock_token, mock_config):
        mock_token.return_value = 'foo'
        mock_config.return_value = self.CONFIG
        url = re.compile('^https://www.sbs.com.au/api/v3/video_favourite/rem')
        params = {'action': 'removefavourites', 'entry_type': 'TVSeries',
                  'program_id': '6000'}
        responses.add(responses.GET, url,
                      body=self.VIDEO_FAVOURITE_REMOVE_JSON,
                      status=200)
        observed = comm.remove_from_favourites(params)
        self.assertIs(True, observed)

    @mock.patch('uuid.uuid4')
    @mock.patch('resources.lib.comm.get_login_token')
    @mock.patch('xbmcaddon.Addon', fakes.FakeAddon)
    @responses.activate
    def test_get_stream(self, mock_token, mock_uuid):
        mock_uuid.side_effect = fakes.UUID
        mock_token.return_value = 'foo'
        program_id = '1234'
        url = re.compile('^https://www.sbs.com.au/api/v3/video_stream')
        responses.add(responses.GET, url,
                      body=self.VIDEO_STREAM_JSON,
                      status=200)
        observed = comm.get_stream(program_id)
        self.assertEqual({'stream_url': 'https://foo.bar/content.m3u8'},
                         observed)
