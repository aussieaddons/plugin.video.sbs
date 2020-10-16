from __future__ import absolute_import, unicode_literals

from collections import OrderedDict
from datetime import datetime

try:
    import mock
except ImportError:
    import unittest.mock as mock

import testtools

import resources.lib.classes as classes


class ClassesSeriesTests(testtools.TestCase):

    def test_get_sort_title(self):
        s = classes.Series()
        s.title = 'The Foo'
        observed = s.get_sort_title()
        expected = 'foo'
        self.assertEqual(expected, observed)

    def test_get_list_title(self):
        s = classes.Series()
        s.title = 'Foo Bar'
        s.num_episodes = 3
        observed = s.get_list_title()
        expected = 'Foo Bar (3)'
        self.assertEqual(expected, observed)

    def test_get_season(self):
        pass

    def test_get_extended_description(self):
        pass

    def test_get_kodi_list_item(self):
        pass

    def test_make_kodi_url(self):
        pass

    def test_parse_kodi_url(self):
        pass


class ClassesProgramTests(testtools.TestCase):

    def test_get_list_title_season_episode(self):
        p = classes.Program()
        p.series_title = 'Foobar'
        p.season_no = 3
        p.episode_no = 10
        observed = p.get_list_title()
        expected = 'Foobar - S03E10'
        self.assertEqual(expected, observed)

    def test_get_list_title_season_episode_title(self):
        p = classes.Program()
        p.series_title = 'Foobar'
        p.season_no = '3'
        p.title = 'Revenge of Spam'
        observed = p.get_list_title()
        expected = 'Foobar - S03 - Revenge of Spam'
        self.assertEqual(expected, observed)

    def test_get_list_title_episode(self):
        p = classes.Program()
        p.title = 'Foobar'
        p.episode_no = 10
        observed = p.get_list_title()
        expected = 'Foobar - E10'
        self.assertEqual(expected, observed)

    def test_get_list_title_season(self):
        p = classes.Program()
        p.title = 'Foobar'
        p.season_no = 3
        observed = p.get_list_title()
        expected = 'Foobar - S03'
        self.assertEqual(expected, observed)

    def test_get_description(self):
        p = classes.Program()
        p.description = 'Foo kills Bar'
        p.expire = datetime(2019, 8, 13)
        observed = p.get_description()
        expected = 'Foo kills Bar\n\nExpires: Tue, 13 Aug 2019'
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    def test_get_duration_isengard(self, mock_version):
        mock_version.return_value = 15
        p = classes.Program()
        p.duration = '903'
        observed = p.get_duration()
        expected = 903
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    def test_get_duration_helix(self, mock_version):
        mock_version.return_value = 14
        p = classes.Program()
        p.duration = '903'
        observed = p.get_duration()
        expected = 15
        self.assertEqual(expected, observed)

    def test_get_date(self):
        p = classes.Program()
        p.date = datetime(2019, 8, 13)
        observed = p.get_date()
        expected = '2019-08-13'
        self.assertEqual(expected, observed)

    def test_parse_date(self):
        date_string = '2019-12-04T10:35:00Z'
        observed = classes.Program.parse_date(date_string)
        expected = datetime(2019, 12, 4, 10, 35, 0)
        self.assertEqual(expected, observed)

    def test_get_date_empty(self):
        p = classes.Program()
        date_string = None
        observed = p.get_date(date_string)
        self.assertEqual(None, observed)

    def test_get_date_as_datetime(self):
        p = classes.Program()
        p.date = '2019-12-04T10:35:00Z'
        observed = p.get_date(as_datetime=True)
        expected = datetime(2019, 12, 4, 10, 35, 0)
        self.assertEqual(expected, observed)

    def test_get_expire(self):
        p = classes.Program()
        p.expire = datetime(2019, 8, 13, 0, 0, 0)
        observed = p.get_expire()
        expected = '2019-08-13 00:00:00'
        self.assertEqual(expected, observed)

    def test_get_subfilename(self):
        p = classes.Program()
        p.subfilename = 'subtitles_en'
        observed = p.get_subfilename()
        expected = 'subtitles_en.SRT'
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    def test_get_kodi_list_item(self, mock_version):
        mock_version.return_value = 15
        p = classes.Program()
        p.title = 'Foo'
        p.series_title = 'Return of Foo'
        p.season_no = 2
        p.duration = '100'
        p.date = datetime(2019, 8, 13, 20, 1, 23)
        observed = p.get_kodi_list_item()
        expected = {
            'tvshowtitle': 'Return of Foo',
            'title': 'Return of Foo - S02 - Foo',
            'duration': 100,
            'year': 2019,
            'aired': '2019-08-13',
            'season': 2,
            'mediatype': 'episode'
        }
        self.assertEqual(expected, observed)

    def test_make_kodi_url(self):
        attrs = {'rating': 'PG',
                 'obj_type': 'Program',
                 'description': "Stuff happens",
                 'episode_no': 1,
                 'entry_type': 'Episode',
                 'title': 'Re-Launch',
                 'season_no': 2,
                 'series_title': 'New Girl',
                 'id': '1604589635977',
                 'thumb': 'https://foo.bar/image.jpg'}
        expected = (
            'description=Stuff+happens&entry_type=Episode&episode_no=1&id'
            '=1604589635977&obj_type=Program&rating=PG&season_no=2'
            '&series_title=New+Girl&thumb=https%3A%2F%2Ffoo.bar%2Fimage.jpg'
            '&title=Re-Launch')
        p = classes.Program()
        attrs = OrderedDict(
            sorted(attrs.items(), key=lambda x: x[0]))
        for k, v in attrs.items():
            setattr(p, k, v)
        p.__dict__.pop('date')  # do we still need the date attrib?
        observed = p.make_kodi_url()
        self.assertEqual(expected, observed)

    def test_parse_kodi_url(self):
        url = (
            'date=2019-12-04T10%3A35%3A00Z&description=Stuff+happens'
            '&entry_type=Episode&episode_no=1&id=1604589635977'
            '&obj_type=Program&rating=PG&season_no=2'
            '&series_title=New+Girl&thumb=https%3A%2F%2Ffoo.bar%2Fimage.jpg'
            '&title=Re-Launch')
        p = classes.Program()
        p.parse_kodi_url(url)
        observed = p.make_kodi_url()
        self.assertEqual(url, observed)
