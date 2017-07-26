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
import config
import os
import sys
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def play(url):
    addon = xbmcaddon.Addon()

    try:
        p = classes.Program()
        p.parse_xbmc_url(url)

        # Some programs don't have protected streams. 'Public' streams are
        # set in program.url, otherwise we fetch it separately
        if p.get_url():
            stream_url = p.get_url()
        else:
            stream_url = comm.get_stream(p.id)

        listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                    iconImage=p.thumbnail,
                                    thumbnailImage=p.thumbnail,
                                    path=stream_url)
        listitem.setInfo('video', p.get_xbmc_list_item())

        # Add subtitles if available
        if addon.getSetting('subtitles_enabled') == 'true' and \
                p.get_subfilename():
            subtitles = None
            profile = xbmcaddon.Addon().getAddonInfo('profile')
            path = xbmc.translatePath(profile).decode('utf-8')
            if not os.path.isdir(path):
                os.makedirs(path)
            subfile = xbmc.translatePath(os.path.join(path,
                                                      'subtitles.eng.srt'))
            if os.path.isfile(subfile):
                os.remove(subfile)
            x = stream_url.find('managed')+8
            subdate = stream_url[x:x+11]
            suburl = config.subtitle_url+subdate+p.get_subfilename()
            try:
                data = urllib2.urlopen(suburl).read()
                f = open(subfile, 'w')
                f.write(data)
                f.close()
                if hasattr(listitem, 'setSubtitles'):
                    # This function only supported from Kodi v14+
                    listitem.setSubtitles([subfile])
                else:
                    subtitles = True
            except Exception:
                utils.log('Subtitles not available for this program')

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
            listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

        # Enable subtitles for XBMC v13
        if addon.getSetting('subtitles_enabled') == "true" and \
                p.get_subfilename():
            if subtitles:
                if not hasattr(listitem, 'setSubtitles'):
                    player = xbmc.Player()
                    while not player.isPlaying():
                        xbmc.sleep(100)  # wait until video is being played
                        player.setSubtitles(subfile)
    except Exception:
        utils.handle_error("Unable to play video")
