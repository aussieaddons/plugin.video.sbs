import classes
import comm
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils
from aussieaddonscommon import session


def play(url):
    try:
        addon = xbmcaddon.Addon()
        p = classes.Program()
        p.parse_xbmc_url(url)
        stream_info = comm.get_stream(p.id)
        if not stream_info:
            return
        stream_url = stream_info.get('stream_url')


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
                sess = session.Session()
                data = sess.get(sub_url).text
                f = open(subfile, 'w')
                f.write(data)
                f.close()
                if hasattr(listitem, 'setSubtitles'):
                    # This function only supported from Kodi v14+
                    listitem.setSubtitles([subfile])
            except Exception:
                utils.log('Subtitles not available for this program')


        listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
        listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
        listitem.setProperty('inputstream.adaptive.license_key', stream_url)

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error("Unable to play video")
