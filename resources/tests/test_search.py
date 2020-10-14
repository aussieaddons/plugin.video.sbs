from __future__ import absolute_import, unicode_literals

import json

try:
    import mock
except ImportError:
    import unittest.mock as mock


import responses

import testtools

import resources.lib.search as search
from resources.tests.fakes import fakes


class SearchTests(testtools.TestCase):

    @mock.patch('resources.lib.search.addon', fakes.FakeAddon(
        SEARCH_HISTORY='["foo", "bar", "FOOBAR"]'))
    def test_get_search_history(self):
        expected = ['foo', 'bar', 'FOOBAR']
        observed = search.get_search_history()
        self.assertEqual(expected, observed)

    @mock.patch('xbmcgui.Dialog.input')
    @mock.patch('resources.lib.search.add_to_search_history')
    @responses.activate
    def test_get_search_input(self, mock_add, mock_input):
        mock_input.return_value = 'foobar'
        mock_resources = mock.MagicMock()
        with mock.patch.dict('sys.modules', {'resources': mock_resources}):
            search.get_search_input()
            mock_resources.lib.index.make_search_list.assert_called_once_with(
                {'name': 'foobar'})
            mock_add.assert_called_once_with('foobar')

    @mock.patch('resources.lib.search.addon', new_callable=fakes.FakeAddon)
    def test_set_search_history(self, mock_addon):
        search.set_search_history(['foo', 'bar', 'FOOBAR'])
        self.assertEqual('["foo", "bar", "FOOBAR"]',
                         mock_addon.getSetting('SEARCH_HISTORY'))

    @mock.patch('resources.lib.search.get_search_history')
    def test_get_search_history_listing(self, mock_history):
        mock_history.return_value = ['foo', 'bar', 'FOOBAR']
        observed = search.get_search_history_listing()
        expected = ['New Search', 'foo', 'bar', 'FOOBAR']
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.search.addon', new_callable=fakes.FakeAddon)
    @mock.patch('resources.lib.search.get_search_history')
    def test_add_to_search_history(self, mock_history, mock_addon):
        mock_history.return_value = ['foo', 'bar', 'FOOBAR']
        search.add_to_search_history('Baz')
        observed = json.loads(mock_addon.getSetting('SEARCH_HISTORY'))
        expected = ['foo', 'bar', 'FOOBAR', 'Baz']
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.search.addon', new_callable=fakes.FakeAddon)
    @mock.patch('resources.lib.search.get_search_history')
    def test_remove_from_search_history(self, mock_history, mock_addon):
        mock_history.return_value = ['foo', 'bar', 'FOOBAR']
        search.remove_from_search_history('foo')
        observed = json.loads(mock_addon.getSetting('SEARCH_HISTORY'))
        expected = ['bar', 'FOOBAR']
        self.assertEqual(expected, observed)
