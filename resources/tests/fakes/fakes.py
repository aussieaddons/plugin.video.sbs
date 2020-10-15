# coding=utf-8
from past.builtins import basestring

import xbmcaddon

import xbmcgui


class FakeAddon(xbmcaddon.Addon):
    def __init__(self, user_token='', unique_id='', ad_id='', **kwargs):
        super(FakeAddon, self).__init__()
        self.__dict__.update(kwargs)
        self.user_token = user_token
        self.unique_id = unique_id
        self.ad_id = ad_id

    def getSetting(self, setting):
        return getattr(self, setting, '')

    def setSetting(self, setting, value):
        setattr(self, setting, value)


class FakeListItem(xbmcgui.ListItem):
    def __init__(self, label="", label2="", iconImage="", thumbnailImage="",
                 path="", offscreen=False):
        super(FakeListItem, self).__init__()
        self.setLabel(label)
        self.setLabel2(label2)
        self.setIconImage(iconImage)
        self.setThumbnailImage(thumbnailImage)
        self.setPath(path)
        self.offscreen = offscreen
        self.art = {}
        self.defaultRating = ''
        self.info = {}
        self.rating = {}
        self.streamInfo = {}
        self.property = {}
        self.subtitles = None
        self.uniqueid = {}
        self.context_items = []

    def setLabel(self, label):
        assert isinstance(label, basestring)
        self.label = label

    def setLabel2(self, label):
        self.label2 = label

    def setIconImage(self, iconImage):
        self.iconImage = iconImage

    def setThumbnailImage(self, thumbFilename):
        self.thumbFilename = thumbFilename

    def setArt(self, dictionary):
        allowed_keys = [
            'thumb',
            'poster',
            'banner',
            'fanart',
            'clearart',
            'clearlogo',
            'landscape',
            'icon'
        ]
        for k, v in dictionary.items():
            if k not in allowed_keys:
                raise Exception('Unallowed key for setArt')
            self.art.update({k: v})

    def setIsFolder(self, isFolder):
        assert type(isFolder) == bool
        self.is_folder = isFolder

    def setUniqueIDs(self, values, defaultrating=''):
        allowed_keys = [
            'imdb',
            'tvdb',
            'tmdb',
            'anidb'
        ]
        if defaultrating:
            assert defaultrating in allowed_keys
            self.defaultRating = defaultrating
        for k, v in values.items():
            assert k in allowed_keys
            self.uniqueid.update({k: v})

    def setRating(self, type, rating, votes=0, default=False):
        assert isinstance(type, basestring)
        assert isinstance(rating, (int, float))
        assert isinstance(votes, int)
        assert isinstance(default, bool)
        self.rating.update({'type': type, 'rating': rating, 'votes': votes,
                            'default': default})

    def addContextMenuItems(self, items, replaceItems=False):
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, tuple)
            for subitem in item:
                assert isinstance(subitem, basestring)
            self.context_items.append(item)

    def addSeason(self, number, name=''):
        assert isinstance(number, int)
        assert isinstance(name, basestring)

    def setInfo(self, type, infoLabels):
        self.info.update(infoLabels)

    def addStreamInfo(self, cType, dictionary):
        self.streamInfo.update({cType: dictionary})

    def setProperty(self, key, value):
        self.property.update({key: value})

    def setProperties(self, dictionary):
        self.property.update(dictionary)

    def setPath(self, path):
        assert isinstance(path, (str, bytes))
        self.path = path

    def setSubtitles(self, subtitleFiles):
        assert isinstance(subtitleFiles, list)
        self.subtitles = subtitleFiles

    def getLabel(self):
        return self.label

    def getPath(self):
        return self.path


class FakePlugin(object):
    def __init__(self):
        self.SORT_METHOD_LABEL = 1
        self.SORT_METHOD_LABEL_IGNORE_THE = 2
        self.SORT_METHOD_NONE = 0
        self.SORT_METHOD_TITLE = 9
        self.SORT_METHOD_TITLE_IGNORE_THE = 10
        self.SORT_METHOD_UNSORTED = 40
        self.SORT_METHOD_VIDEO_SORT_TITLE = 26
        self.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE = 27
        self.SORT_METHOD_VIDEO_TITLE = 25
        self.SORT_METHOD_EPISODE = 24
        self.directory = []
        self.resolved = None

    def addDirectoryItem(self, handle, url, listitem, isFolder=False,
                         totalItems=0):
        assert isinstance(url, (str, bytes))
        self.directory.append(
            {'handle': handle, 'url': url, 'listitem': listitem,
             'isFolder': isFolder})

    def addDirectoryItems(self, handle, items, totalItems=0):
        for item in items:
            self.addDirectoryItem(handle, item[0], item[1],
                                  item[2] if len(item) == 3 else False,
                                  totalItems)

    def endOfDirectory(self, handle, succeeded=True, updateListing=False,
                       cacheToDisc=True):
        self.end = True

    def setResolvedUrl(self, handle, succeeded, listitem):
        self.resolved = (handle, succeeded, listitem)

    def addSortMethod(self, handle, sortMethod, label2Mask=''):
        pass

    def setContent(self, handle, content):
        self.content = content


UUID = [
    'e8485af7-fe81-4064-bfb0-fdafbf68db33',
    'cea23fb2-ab9d-4869-8b01-fdb66aab09e7'
]

LOGIN = ['foo', 'bar']

LOGIN_TOKEN = ('YW5kcm9pZDJhMzIxZTQ1NDhjMzMzMGRhZmE4ZmNhODk4ZWYxNDEyNmZkMj'
               'IwMmU6YW5kcm9pZA==')
