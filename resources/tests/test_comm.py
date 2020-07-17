from __future__ import absolute_import, unicode_literals

import io
import json
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import quote_plus

import requests

import responses

import testtools

import resources.lib.comm as comm
import resources.lib.config as config
#from resources.tests.fakes import fakes


class CommTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/hero.json'), 'rb') as f:
            self.HERO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_config.json'), 'rb') as f:
            self.VIDEO_CONFIG_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_favourite_all.json'), 'rb') as f:
            self.VIDEO_FAV_ALL_JSON = io.BytesIO(f.read()).read()

    @responses.activate
    def test_get_entries_hero(self):
        responses.add(responses.GET, 'https://foo.bar/hero&range=1-50',
                      body=self.HERO_JSON,
                      status=200)
        params = {'item_type': 'hero', 'obj_type': 'Series',
                  'feed_url': 'https://foo.bar/hero', 'title': 'Hero carousel'}
        listing = comm.get_entries(params)

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
