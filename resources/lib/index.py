import classes
import comm
import sys
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_index_list():
    try:
        index = comm.get_index()['contentStructure'].get('menu')
        ok = True
        for i in index:
            if i == 'Search':  # implement at a later stage
                continue
            url = "%s?%s" % (sys.argv[0], utils.make_url({
                             'category': i}))
            listitem = xbmcgui.ListItem(i)
            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url, listitem=listitem,
                                             isFolder=True)

        listitem = xbmcgui.ListItem(label='Settings')
        ok = xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url="{0}?action=settings".format(sys.argv[0]),
            listitem=listitem,
            isFolder=False)

        if not xbmcaddon.Addon().getSetting('user_token'):
            listitem = xbmcgui.ListItem(label='Login')
            ok = xbmcplugin.addDirectoryItem(
                handle=int(sys.argv[1]),
                url="{0}?action=login".format(sys.argv[0]),
                listitem=listitem,
                isFolder=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]),
                                  succeeded=ok,
                                  cacheToDisc=False)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to build index')


def make_entries_list(params):
    utils.log('Making entries list')
    try:
        programs = comm.get_entries(params)

        ok = True
        for p in sorted(programs):
            listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                        iconImage=p.get_thumbnail(),
                                        thumbnailImage=p.get_thumbnail())
            if type(p) is classes.Program:
                listitem.setInfo('video', p.get_kodi_list_item())
                listitem.setProperty('IsPlayable', 'true')


                listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
                listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

                # Build the URL for the program, including the list_info
            url = '{0}?{1}'.format(sys.argv[0], p.make_kodi_url())
            # Add the program item to the list
            isFolder = type(p) is classes.Series
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                             listitem=listitem, isFolder=isFolder,
                                             totalItems=len(programs))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to fetch entries list')


def make_category_list(params):
    utils.log("Making category list")
    try:

        categories = comm.get_category(params)
        ok = True
        for c in categories:
            url = '{0}?{1}'.format(sys.argv[0], c.make_kodi_url())
            thumb = c.get_thumbnail()
            listitem = xbmcgui.ListItem(label=c.get_list_title())
            listitem.setArt({'thumb': thumb,
                             'icon': thumb})
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to build categories list')


def make_genre_categories(params):
    utils.log("Making genre category list")
    try:
        genre_categories = comm.get_entries(params)
        ok = True
        for c in genre_categories:
            url = '{0}?{1}'.format(sys.argv[0], c.make_kodi_url())
            thumb = c.get_thumbnail()
            listitem = xbmcgui.ListItem(label=c.get_list_title())
            listitem.setArt({'thumb': thumb,
                             'icon': thumb})
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to build genre categories list')
