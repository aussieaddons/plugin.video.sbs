import sys

from future.moves.urllib.parse import quote_plus

from aussieaddonscommon import utils

import resources.lib.classes as classes
import resources.lib.comm as comm
import resources.lib.search as search

import xbmcaddon

import xbmcplugin

addon = xbmcaddon.Addon()


def make_index_list():
    try:
        index = comm.get_config()['contentStructure'].get('menu')
        ok = True
        for i in index:
            url = "%s?%s" % (sys.argv[0], utils.make_url({
                             'category': i}))
            listitem = comm.create_listitem(i)
            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=str(url), listitem=listitem,
                                             isFolder=True)

        listitem = comm.create_listitem(label='Favourites')
        ok = xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url="{0}?action=favouritescategories".format(sys.argv[0]),
            listitem=listitem,
            isFolder=True)

        listitem = comm.create_listitem(label='Settings')
        ok = xbmcplugin.addDirectoryItem(
            handle=int(sys.argv[1]),
            url="{0}?action=settings".format(sys.argv[0]),
            listitem=listitem,
            isFolder=False)

        if not addon.getSetting('user_token'):
            listitem = comm.create_listitem(label='Login')
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
        items = []
        for p in programs:
            listitem = comm.create_listitem(label=p.get_list_title())

            if isinstance(p, classes.Program):
                listitem.setInfo('video', p.get_kodi_list_item())
                listitem.setProperty('IsPlayable', 'true')
                listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
                listitem.addStreamInfo('video', p.get_kodi_video_stream_info())
                # Build the URL for the program, including the list_info
            elif isinstance(p, classes.Series):
                if p.page_begin and p.page_size:
                    listitem.setProperty('SpecialSort', 'bottom')
                else:
                    listitem.setInfo('video', p.get_kodi_list_item())
            thumb = p.get_thumb()
            listitem.setArt({'thumb': thumb,
                             'icon': thumb,
                             'fanart': p.get_fanart()})
            url = '{0}?{1}'.format(sys.argv[0], p.make_kodi_url())
            # Add the program item to the list
            isFolder = isinstance(p, classes.Series)
            if p.entry_type in ['TVSeries', 'Movie', 'OneOff']:
                if params.get('favourite'):
                    listitem.addContextMenuItems([(
                        'Remove from SBS favourites',
                        ('RunPlugin(plugin://plugin.video.sbs/?action=remove'
                            'favourites&program_id={0}&entry_type={1})'.format(
                                p.id, p.entry_type))
                    )])
                else:
                    listitem.addContextMenuItems([(
                        'Add to SBS favourites',
                        ('RunPlugin(plugin://plugin.video.sbs/?action=add'
                            'favourites&program_id={0}&entry_type={1})'.format(
                                p.id, p.entry_type))
                    )])

            items.append((url, listitem, isFolder))

        xbmcplugin.addSortMethod(
            int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.addSortMethod(
            int(sys.argv[1]), xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.addSortMethod(
            int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE_IGNORE_THE)

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
        categories = comm.get_category(params)
        ok = True
        for c in categories:
            url = '{0}?{1}'.format(sys.argv[0], c.make_kodi_url())
            thumb = c.get_thumb()
            listitem = comm.create_listitem(label=c.get_list_title())
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


def make_search_history_list():
    try:
        listing = search.get_search_history_listing()
        ok = True
        for item in listing:
            listitem = comm.create_listitem(label=item)
            listitem.setInfo('video', {'plot': ''})
            listitem.addContextMenuItems([(
                'Remove from search history',
                ('RunPlugin(plugin://plugin.video.sbs/?action=remove'
                    'search&name={0})'.format(item))
            )])
            url = "{0}?action=searchhistory&name={1}".format(
                sys.argv[0], quote_plus(item))

            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok,
                                  cacheToDisc=False)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error('Unable to fetch search history list')


def make_search_list(params):
    try:
        listing = comm.get_search_results(params)
        ok = True
        for s in listing:
            url = "{0}?action=series_list&{1}".format(sys.argv[0],
                                                      s.make_kodi_url())
            thumb = s.get_thumb()
            listitem = comm.create_listitem(s.get_list_title())
            listitem.setArt({'icon': thumb,
                             'thumb': thumb})
            listitem.setInfo('video', {'plot': s.get_description()})
            folder = False
            if isinstance(s, classes.Program):
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
        utils.handle_error('Unable to fetch search list')


def make_favourites_categories_list():
    utils.log("Making favourites category list")
    try:
        favourites_categories = comm.get_favourites_categories()
        ok = True
        for c in favourites_categories:
            url = '{0}?{1}'.format(sys.argv[0], c.make_kodi_url())

            listitem = comm.create_listitem(label=c.get_list_title())
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to build favourites categories list')
