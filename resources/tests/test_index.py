from __future__ import absolute_import, unicode_literals

import io
import json
import os
import re
import sys

try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes


class IndexTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/video_config.json'),
                  'rb') as f:
            self.VIDEO_CONFIG_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_all.json'),
                  'rb') as f:
            self.VIDEO_FAV_ALL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_feed.json'), 'rb') as f:
            self.VIDEO_FEED_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/json/video_program_collection.json'),
                'rb') as f:
            self.VIDEO_PROGRAM_COLLECTION_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_search_movies.json'),
                  'rb') as f:
            self.VIDEO_SEARCH_MOVIES_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_stream.json'),
                  'rb') as f:
            self.VIDEO_STREAM_JSON = io.BytesIO(f.read()).read()

    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '',
                 'resume:false'])
    @responses.activate
    def test_make_index_list_not_logged_in(self, mock_listitem, mock_version):
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            index.make_index_list()
            observed = []
            expected = ['Featured', 'Programs', 'Movies', 'Catchup',
                        'Search', 'Favourites', 'Settings', 'Login']
            for res in mock_plugin.directory:
                observed.append(res.get('listitem').getLabel())

            self.assertEqual(expected, observed)

    @mock.patch('xbmcaddon.Addon')
    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '',
                 'resume:false'])
    @responses.activate
    def test_make_index_list_logged_in(self, mock_listitem, mock_version,
                                       mock_addon):
        mock_addon.return_value = fakes.FakeAddon(user_token='foo')
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            index.make_index_list()
            observed = []
            expected = ['Featured', 'Programs', 'Movies', 'Catchup',
                        'Search', 'Favourites', 'Settings']
            for res in mock_plugin.directory:
                observed.append(res.get('listitem').getLabel())

            self.assertEqual(expected, observed)

    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?feed_url=http%3a%2f%2ffoo.bar%2fapi%2fv3%2fvideo_feed'
                 '&obj_type=Series&title=Season%202',
                 'resume:false'])
    @responses.activate
    def test_make_entries_list(self, mock_listitem, mock_version):
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        feed_url = 'http://foo.bar/api/v3/video_feed&range=1-50'
        responses.add(responses.GET, feed_url,
                      body=self.VIDEO_FEED_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            params = index.utils.get_url(sys.argv[2][1:])
            index.make_entries_list(params)
            observed = []
            for res in mock_plugin.directory:
                observed.append(res.get('listitem').getLabel())

            self.assertEqual(18, len(observed))
            self.assertIn('New Girl - S02E12 - Cabin', observed)

    @mock.patch('xbmcaddon.Addon')
    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?feed_url=http%3a%2f%2ffoo.bar%2fapi%2fv3%2fvideo_program'
                 '&obj_type=Series&title=Something',
                 'resume:false'])
    @responses.activate
    def test_make_entries_list_context_items(
            self, mock_listitem, mock_version, mock_addon):
        mock_addon.return_value = fakes.FakeAddon(user_token='foo')
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        feed_url = 'http://foo.bar/api/v3/video_program&range=1-50'
        responses.add(responses.GET, feed_url,
                      body=self.VIDEO_PROGRAM_COLLECTION_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            params = index.utils.get_url(sys.argv[2][1:])
            index.make_entries_list(params)
            observed = []
            for res in mock_plugin.directory:
                if res.get('listitem').context_items:
                    observed.extend(res.get('listitem').context_items)
            self.assertEqual(27, len(observed))
            seen = False
            for item in observed:
                if '3236' in item[1]:
                    seen = True
            self.assertIs(True, seen)

    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?category=Programs',
                 'resume:false'])
    @responses.activate
    def test_make_category_list(self, mock_listitem, mock_version):
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            params = index.utils.get_url(sys.argv[2][1:])
            index.make_category_list(params)
            observed = []
            for res in mock_plugin.directory:
                observed.append(res.get('listitem').getLabel())

            self.assertEqual(18, len(observed))
            self.assertIn('Spy Series', observed)

    @mock.patch('resources.lib.search.get_search_history')
    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?category=Search',
                 'resume:false'])
    def test_make_search_history_list(self, mock_listitem, mock_version,
                                      mock_history):
        mock_history.return_value = ['Foo', 'Bar', 'foobar']
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            index.make_search_history_list()
            observed = []
            for res in mock_plugin.directory:
                observed.append(res.get('listitem').getLabel())
            self.assertEqual(['New Search', 'Foo', 'Bar', 'foobar'],
                             observed)

    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=searchhistory&name=news',
                 'resume:false'])
    @responses.activate
    def test_make_search_list(self, mock_listitem, mock_version):
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        feed_url = re.compile('https://www.sbs.com.au/api/v3/video_search')
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON)
        responses.add(responses.GET, feed_url,
                      body=self.VIDEO_SEARCH_MOVIES_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            params = index.utils.get_url(sys.argv[2][1:])
            index.make_search_list(params)
            observed = []
            for res in mock_plugin.directory:
                observed.append(res.get('listitem').getLabel())
            self.assertEqual(['Live (3)', 'Programs (3)', 'Movies (3)',
                              'Clips (3)', 'Episodes (3)'], observed)

    @mock.patch('resources.lib.comm.get_favourites_data')
    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=favouritescategories',
                 'resume:false'])
    @responses.activate
    def test_make_favourites_categories_list(
            self, mock_listitem, mock_version, mock_favourites):
        mock_favourites.return_value = json.loads(self.VIDEO_FAV_ALL_JSON)
        mock_version.return_value = 18
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            index.make_favourites_categories_list()
            observed = []
            for res in mock_plugin.directory:
                observed.append(res.get('listitem').getLabel())
            self.assertEqual(['Programs'], observed)
