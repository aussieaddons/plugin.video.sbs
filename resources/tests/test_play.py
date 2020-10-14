from __future__ import absolute_import, unicode_literals

import io
import os
import re
import sys

try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

from resources.tests.fakes import fakes


class PlayTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/video_stream.json'),
                  'rb') as f:
            self.VIDEO_STREAM_JSON = io.BytesIO(f.read()).read()

    @mock.patch('aussieaddonscommon.utils.get_kodi_major_version')
    @mock.patch('resources.lib.comm.get_login_token')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.sbs/', '5',
                 '?date=2019-09-30T14:00:00Z&entry_type=Episode'
                 '&expire=2020-10-26T04:05:00Z&id=1604589635977'
                 '&obj_type=Program&season_no=2&series_title=New+Girl'
                 '&title=Re-Launch',
                 'resume:false'])
    @responses.activate
    def test_play(self, mock_listitem, mock_token, mock_version):
        mock_version.return_value = 18
        mock_token.return_value = 'foo'
        mock_plugin = fakes.FakePlugin()
        mock_listitem.side_effect = fakes.FakeListItem
        url = re.compile('^https://www.sbs.com.au/api/v3/video_stream')
        responses.add(responses.GET, url, body=self.VIDEO_STREAM_JSON)
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.play as play
            play.play(sys.argv[2][1:])
            expected = 'New Girl - S02 - Re-Launch'
            observed = mock_plugin.resolved[2].getLabel()
            self.assertEqual(expected, observed)
