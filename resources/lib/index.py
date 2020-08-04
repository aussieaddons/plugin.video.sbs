import classes
import comm
import sys
import time
import xbmcaddon
import xbmcgui
import xbmcplugin

from future.moves.urllib.parse import quote_plus

from aussieaddonscommon import utils

import resources.lib.search as search


def make_index_list():
    try:
        ver = utils.get_kodi_major_version()
        index = comm.get_config()['contentStructure'].get('menu')
        ok = True
        for i in index:
            url = "%s?%s" % (sys.argv[0], utils.make_url({
                             'category': i}))
            if ver >= 18:
                listitem = xbmcgui.ListItem(i, offscreen=True)
            else:
                listitem = xbmcgui.ListItem(i)
            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url, listitem=listitem,
                                             isFolder=True)

        listitem = xbmcgui.ListItem(label='Favourites')
        ok = xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url="{0}?action=favouritescategories".format(sys.argv[0]),
            listitem=listitem,
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
        ver = utils.get_kodi_major_version()
        programs = comm.get_entries(params)
        t = time.time()
        ok = True
        items = []
        for p in programs:
            if ver >= 18:
                listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                            offscreen=True)
            else:
                listitem = xbmcgui.ListItem(label=p.get_list_title())
            if type(p) is classes.Program:
                listitem.setInfo('video', p.get_kodi_list_item())
                listitem.setProperty('IsPlayable', 'true')
                listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
                listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

                # Build the URL for the program, including the list_info
            thumb = p.get_thumb()
            listitem.setArt({'thumb': thumb,
                             'icon': thumb,
                             'fanart': p.get_fanart()})
            url = '{0}?{1}'.format(sys.argv[0], p.make_kodi_url())
            # Add the program item to the list
            isFolder = type(p) is classes.Series
            if p.entry_type in ['TVSeries', 'Movie', 'OneOff']:
                if params.get('favourite'):
                    listitem.addContextMenuItems(
                        [('Remove from SBS favourites',
                          ('RunPlugin(plugin://plugin.video.sbs/?action=remove'
                           'favourites&program_id={0}&entry_type={1})'.format(
                              p.id, p.entry_type
                          )))])
                else:
                    listitem.addContextMenuItems(
                        [('Add to SBS favourites',
                          ('RunPlugin(plugin://plugin.video.sbs/?action=add'
                           'favourites&program_id={0}&entry_type={1})'.format(
                              p.id, p.entry_type
                          )))])

            items.append((url, listitem, isFolder))

        xbmcplugin.addSortMethod(
            int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.addSortMethod(
            int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        ok = xbmcplugin.addDirectoryItems(handle=int(sys.argv[1]),
                                          items=items,
                                          totalItems=len(items))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to fetch entries list')


def make_category_list(params):
    utils.log("Making category list")
    try:
        ver = utils.get_kodi_major_version()
        categories = comm.get_category(params)
        ok = True
        for c in categories:
            url = '{0}?{1}'.format(sys.argv[0], c.make_kodi_url())
            thumb = c.get_thumb()
            if ver >= 18:
                listitem = xbmcgui.ListItem(label=c.get_list_title(),
                                            offscreen=True)
            else:
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
        ver = utils.get_kodi_major_version()
        genre_categories = comm.get_entries(params)
        ok = True
        for c in genre_categories:
            url = '{0}?{1}'.format(sys.argv[0], c.make_kodi_url())
            thumb = c.get_thumb()
            if ver >= 18:
                listitem = xbmcgui.ListItem(label=c.get_list_title(),
                                            offscreen=True)
            else:
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


def make_search_history_list():
    try:
        listing = search.get_search_history_listing()
        ok = True
        for item in listing:
            listitem = xbmcgui.ListItem(label=item)
            listitem.setInfo('video', {'plot': ''})
            listitem.addContextMenuItems(
                [('Remove from search history',
                  ('RunPlugin(plugin://plugin.video.sbs/?action=remove'
                   'search&name={0})'.format(item)))])
            url = "{0}?action=searchhistory&name={1}".format(
                sys.argv[0], quote_plus(item))

            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok,
                                  cacheToDisc=False)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception as e:
        utils.handle_error('Unable to fetch search history list')
        raise e


def make_search_list(params):
    try:
        listing = comm.get_search_results(params)
        ok = True
        for s in listing:
            url = "{0}?action=series_list&{1}".format(sys.argv[0],
                                                      s.make_kodi_url())
            thumb = s.get_thumb()
            listitem = xbmcgui.ListItem(s.get_list_title())
            listitem.setArt({'icon': thumb,
                             'thumb': thumb})
            listitem.setInfo('video', {'plot': s.get_description()})
            folder = False
            if type(s) is classes.Program:
                listitem.setProperty('IsPlayable', 'true')
            else:
                folder = True

            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=folder)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error('Unable to fetch search history list')


def make_favourites_categories_list():
    utils.log("Making favourites category list")
    try:
        ver = utils.get_kodi_major_version()
        favourites_categories = comm.get_favourites_categories()
        ok = True
        for c in favourites_categories:
            url = '{0}?{1}'.format(sys.argv[0], c.make_kodi_url())

            if ver >= 18:
                listitem = xbmcgui.ListItem(label=c.get_list_title(),
                                            offscreen=True)
            else:
                listitem = xbmcgui.ListItem(label=c.get_list_title())
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to build favourites categories list')
