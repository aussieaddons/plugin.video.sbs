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

import config
import sys
import comm
import utils
import xbmcgui
import xbmcplugin

def make_section_list(url):
    utils.log("Making section list")
    try:
        params = utils.get_url(url)
        section = comm.get_section(params['category'], params['section'])

        ok = True
        if 'children' in section and len(section['children']) > 0:
            for s in section['children']:
                entries_url = s.get('url')
                if entries_url:
                    url = "%s?%s" % (sys.argv[0],
                               utils.make_url({'entries_url': entries_url}))

                    thumbnail = s.get('thumbnail')
                    listitem = xbmcgui.ListItem(s.get('name'),
                                                iconImage=thumbnail,
                                                thumbnailImage=thumbnail)

                    listitem.setInfo('video',
                                     {'title': s.get('name'),
                                      'genre': s.get('genre'),
                                      'plot': s.get('description'),
                                      'plotoutline': s.get('description')})

                    # Add the program item to the list
                    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                                     url=url,
                                                     listitem=listitem,
                                                     isFolder=True)

        elif 'url' in section:
            # no children, so fetch children by URL
            programs = comm.get_entries(section['url'])
            for p in sorted(programs):
                thumbnail = p.get_thumbnail()
                listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                            iconImage=thumbnail,
                                            thumbnailImage=thumbnail)
                listitem.setInfo('video', p.get_xbmc_list_item())

                if hasattr(listitem, 'addStreamInfo'):
                    listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
                    listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())

                # Build the URL for the program, including the list_info
                url = "%s?play=true&%s" % (sys.argv[0], p.make_xbmc_url())

                # Add the program item to the list
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                                 url=url,
                                                 listitem=listitem,
                                                 isFolder=False,
                                                 totalItems=len(programs))
        else:
            utils.log("No children or url found for %s" % section)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except:
        utils.handle_error()
