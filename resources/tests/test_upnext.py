from __future__ import absolute_import, unicode_literals

import json
from builtins import str as text
from collections import OrderedDict

try:
    import mock
except ImportError:
    import unittest.mock as mock

import testtools

import resources.lib.upnext as upnext


class UpnextTests(testtools.TestCase):

    @mock.patch('resources.lib.upnext.notify')
    def test_upnext_signal(self, mock_notify):
        upnext.upnext_signal(
            'me', OrderedDict({'episodeid': 1234, 'title': 'Baz'}))
        expected_data = ['eyJlcGlzb2RlaWQiOiAxMjM0LCAidGl0bGUiOiAiQmF6In0=']
        mock_notify.assert_called_with(
            sender='me.SIGNAL', message='upnext_data', data=expected_data)

    @mock.patch('resources.lib.upnext.jsonrpc')
    def test_notify(self, mock_jsonrpc):
        mock_jsonrpc.return_value = {'result': 'OK'}
        observed = upnext.notify('me', 'hello', 'stuff')
        self.assertIs(True, observed)

    @mock.patch('xbmc.log')
    @mock.patch('resources.lib.upnext.jsonrpc')
    def test_notify_fail(self, mock_jsonrpc, mock_log):
        mock_jsonrpc.return_value = {
            'result': 'Not OK', 'error': {'message': 'foo'}}
        observed = upnext.notify('me', 'hello', 'stuff')
        self.assertIs(False, observed)
        mock_log.assert_called_once()

    @mock.patch('xbmc.executeJSONRPC')
    def test_jsonrpc(self, mock_execute):
        kwargs = {'foo': 'bar', 'FOO': 'BAZ'}
        mock_execute.return_value = '{"result": "whatever"}'
        upnext.jsonrpc(**kwargs)
        kwargs.update({'id': 0, 'jsonrpc': '2.0'})
        mock_execute.assert_called_with(json.dumps(kwargs, sort_keys=True))

    def test_to_unicode(self):
        observed = upnext.to_unicode('Foo'.encode('utf-8'))
        expected = 'Foo'
        self.assertEqual(observed, expected)
        self.assertIsInstance(observed, text)
