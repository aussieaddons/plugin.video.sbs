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

import classes
import comm
import os
import sys
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def play(url):
    try:
        addon = xbmcaddon.Addon()
        p = classes.Program()
        p.parse_xbmc_url(url)

        # Some programs don't have protected streams. 'Public' streams are
        # set in program.url, otherwise we fetch it separately
        if p.get_url():
            stream_info = {}
            stream_url = p.get_url()
        else:
            stream_info = comm.get_stream(p.id)
            stream_url = stream_info['url']

        bandwidth = addon.getSetting('BANDWIDTH')

        if bandwidth == '0':
            stream_url = stream_url.replace('&b=0-2000', '&b=400-600')
        elif bandwidth == '1':
            stream_url = stream_url.replace('&b=0-2000', '&b=900-1100')
        elif bandwidth == '2':
            stream_url = stream_url.replace('&b=0-2000', '&b=1400-1600')

        listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                    iconImage=p.thumbnail,
                                    thumbnailImage=p.thumbnail,
                                    path=stream_url)
        listitem.setInfo('video', p.get_kodi_list_item())

        # Add subtitles if available
        if 'subtitles' in stream_info:
            sub_url = stream_info['subtitles']
            profile = addon.getAddonInfo('profile')
            path = xbmc.translatePath(profile).decode('utf-8')
            if not os.path.isdir(path):
                os.makedirs(path)
            subfile = xbmc.translatePath(
                os.path.join(path, 'subtitles.eng.srt'))
            if os.path.isfile(subfile):
                os.remove(subfile)
            try:
                data = urllib2.urlopen(sub_url).read()
                f = open(subfile, 'w')
                f.write(data)
                f.close()
                if hasattr(listitem, 'setSubtitles'):
                    # This function only supported from Kodi v14+
                    listitem.setSubtitles([subfile])
            except Exception:
                utils.log('Subtitles not available for this program')

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error("Unable to play video")
