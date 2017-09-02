#
#  SBS On Demand Kodi Add-on
#  Copyright (C) 2015 Andy Botting
#
#  This addon is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This addon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this addon. If not, see <http://www.gnu.org/licenses/>.
#

import comm
import sys
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_category_list(url):
    utils.log("Making category list")
    try:
        params = utils.get_url(url)
        categories = comm.get_category(params['category'])

        ok = True
        if 'children' in categories:
            for c in categories.get('children', []):
                if 'children' in c:
                    url = "%s?%s" % (sys.argv[0], utils.make_url({
                                     'category': params['category'],
                                     'section': c['name']}))
                elif 'url' in c:
                    url = "%s?%s" % (sys.argv[0], utils.make_url({
                                     'entries_url': c['url']}))
                else:
                    continue

                # If no thumbnail, make it an empty string as None makes
                # XBMC v12 with a TypeError must be unicode or str
                thumbnail = c.get('thumbnail', '')
                listitem = xbmcgui.ListItem(label=c['name'],
                                            thumbnailImage=thumbnail)
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                                 url=url,
                                                 listitem=listitem,
                                                 isFolder=True)
        else:
            # 'Coming soon' has no children
            jsonurl = categories['url']
            programs = comm.get_entries(jsonurl)
            for p in sorted(programs):
                thumbnail = p.get_thumbnail()
                listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                            iconImage=thumbnail,
                                            thumbnailImage=thumbnail)
                listitem.setInfo('video', p.get_kodi_list_item())

                if hasattr(listitem, 'addStreamInfo'):
                    listitem.addStreamInfo('audio',
                                           p.get_kodi_audio_stream_info())
                    listitem.addStreamInfo('video',
                                           p.get_kodi_video_stream_info())

                # Build the URL for the program, including the list_info
                url = "%s?play=true&%s" % (sys.argv[0], p.make_xbmc_url())

                # Add the program item to the list
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                                 url=url,
                                                 listitem=listitem,
                                                 isFolder=False,
                                                 totalItems=len(programs))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception as e:
        utils.handle_error('Unable to build categories list', exc=e)
