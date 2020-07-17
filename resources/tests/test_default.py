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

    @mock.patch('resources.lib.comm.get_login_token')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?action=favouritescategories',
                 'resume:false'])
    @responses.activate
    def test_default_favourites_categories(self, mock_listitem, mock_token):
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
