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

    @responses.activate
    def test_get_entries_hero(self):
        responses.add(responses.GET, 'https://foo.bar/hero', body=self.HERO_JSON,
                      status=200)
        params = {'item_type': 'hero', 'obj_type': 'Series',
                  'feed_url': 'https://foo.bar/hero', 'title': 'Hero carousel'}
        listing = comm.get_entries(params)
