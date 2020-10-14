from __future__ import absolute_import, unicode_literals

import importlib
import io
import json
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes

@testtools.skip
class DefaultTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/hero.json'), 'rb') as f:
            self.HERO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_config.json'),
                  'rb') as f:
            self.VIDEO_CONFIG_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_add.json'),
                  'rb') as f:
            self.VIDEO_FAV_ADD_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_all.json'),
                  'rb') as f:
            self.VIDEO_FAV_ALL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_remove.json'),
                  'rb') as f:
            self.VIDEO_FAV_REMOVE_JSON = io.BytesIO(f.read()).read()

    def setUp(self):
        super(DefaultTests, self).setUp()
        self.mock_plugin = fakes.FakePlugin()
        self.patcher = mock.patch.dict('sys.modules',
                                       xbmcplugin=self.mock_plugin)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        for module in ['index', 'play']:
            setattr(self, module,
                    importlib.import_module(
                        'resources.lib.{0}'.format(module)))
            self.assertEqual(self.mock_plugin,
                             getattr(self, module).xbmcplugin)
        global default
        global classes
        default = importlib.import_module('default')
        classes = importlib.import_module('resources.lib.classes')

    def tearDown(self):
        super(DefaultTests, self).tearDown()
        self.patcher.stop()
        self.mock_plugin = None

    @mock.patch('resources.lib.index.make_index_list')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '',
                 'resume:false'])
    def test_default_no_params(self, mock_index_list):
        default.main()
        mock_index_list.assert_called_with()

    @mock.patch('resources.lib.play.play')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?&entry_type=Episode&id=1604589635977&obj_type=Program'
                 '&season_no=2&series_title=New+Girl&title=Re-Launch',
                 'resume:false'])
    def test_default_play(self, mock_play):
        default.main()
        mock_play.assert_called_with(
            '?&entry_type=Episode&id=1604589635977&obj_type=Program'
            '&season_no=2&series_title=New+Girl&title=Re-Launch')

    @mock.patch('resources.lib.index.make_entries_list')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?feed_url=http%3a%2f%2ffoo.bar%2fapi%2fv3%2fvideo_feed'
                 '&obj_type=Series&title=Season%202',
                 'resume:false'])
    def test_default_make_entries(self, mock_entries):
        default.main()
        mock_entries.assert_called_with(
            {'feed_url': 'http://foo.bar/api/v3/video_feed',
             'obj_type': 'Series',
             'title' : 'Season 2'})

    @mock.patch('resources.lib.index.make_category_list')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?item_type=ProgramGenre&obj_type=Series&title=Comedy',
                 'resume:false'])
    def test_default_make_category(self, mock_category):
        default.main()
        mock_category.assert_called_with(
            {'item_type': 'ProgramGenre', 'obj_type': 'Series',
             'title': 'Comedy'})

    @mock.patch('resources.lib.index.make_search_history_list')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?category=Search',
                 'resume:false'])
    def test_default_make_search_history(self, mock_search_history):
        default.main()
        mock_search_history.assert_called_with()

    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('resources.lib.comm.get_login_token')
    @mock.patch('resources.lib.comm.xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=favouritescategories',
                 'resume:false'])
    @responses.activate
    def test_default_favourites_categories(self, mock_listitem, mock_token,
                                           mock_version):
        mock_version.return_value = '18'
        mock_token.return_value = 'foo'
        mock_listitem.side_effect = fakes.FakeListItem
        conf = json.loads(self.VIDEO_CONFIG_JSON)
        fav_all_url = conf.get('favourites').get('listAll')
        responses.add(responses.GET, fav_all_url,
                      body=self.VIDEO_FAV_ALL_JSON,
                      status=200)
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        default.main()
        self.assertEqual(1, len(self.mock_plugin.directory))
        self.assertEqual('Programs', self.mock_plugin.directory[0].get(
            'listitem').getLabel())

    @mock.patch('resources.lib.comm.get_login_token')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=addfavourites&program_id=6000&entry_type=TVSeries',
                 'resume:false'])
    @responses.activate
    def test_default_add_favourites(self, mock_token):
        mock_token.return_value = 'foo'
        conf = json.loads(self.VIDEO_CONFIG_JSON)
        fav_add_url = conf.get('favourites').get('addProgram').replace('[ID]',
                                                                       '6000')
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        responses.add(responses.GET, fav_add_url,
                      body=self.VIDEO_FAV_ADD_JSON,
                      status=200)
        observed = default.main()
        self.assertEqual(True, observed)

    @mock.patch('resources.lib.comm.get_login_token')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=removefavourites&program_id=6000&entry_type'
                 '=TVSeries',
                 'resume:false'])
    @responses.activate
    def test_default_remove_favourites(self, mock_token):
        mock_token.return_value = 'foo'
        conf = json.loads(self.VIDEO_CONFIG_JSON)
        fav_add_url = conf.get('favourites').get('removeProgram').replace(
            '[ID]', '6000')
        responses.add(responses.GET, config.CONFIG_URL,
                      body=self.VIDEO_CONFIG_JSON,
                      status=200)
        responses.add(responses.GET, fav_add_url,
                      body=self.VIDEO_FAV_REMOVE_JSON,
                      status=200)
        observed = default.main()
        self.assertEqual(True, observed)

    @mock.patch('resources.lib.index.make_search_list')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=searchhistory&name=news',
                 'resume:false'])
    def test_default_search_history_list(self, mock_search):
        default.main()
        mock_search.assert_called_with(
            {'action': 'searchhistory', 'name': 'news'})

    @mock.patch('resources.lib.search.get_search_input')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=searchhistory&name=New%20Search',
                 'resume:false'])
    def test_default_search_history_new(self, mock_get_search):
        default.main()
        mock_get_search.assert_called_with()

    @mock.patch('resources.lib.search.remove_from_search_history')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=removesearch&name=news',
                 'resume:false'])
    def test_default_remove_search(self, mock_remove_search):
        default.main()
        mock_remove_search.assert_called_with('news')
