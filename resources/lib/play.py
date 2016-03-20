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

import sys
import classes
import comm
import config
import utils
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

def play(url):
    addon = xbmcaddon.Addon(config.ADDON_ID)

    try:
        p = classes.Program()
        p.parse_xbmc_url(url)

        # Some programs don't have protected streams. 'Public' streams are
        # set in program.url, otherwise we fetch it separately
        if p.get_url():
            stream_url = p.get_url()
        else:
            stream_url = comm.get_stream(p.id)

        listitem=xbmcgui.ListItem(label=p.get_list_title(),
                                  iconImage=p.thumbnail,
                                  thumbnailImage=p.thumbnail,
                                  path=stream_url)
        listitem.setInfo('video', p.get_xbmc_list_item())

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
            listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)
    except:
        utils.handle_error("Unable to play video")
