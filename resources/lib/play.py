import os
import sys
from collections import OrderedDict

from aussieaddonscommon import session
from aussieaddonscommon import utils

import resources.lib.classes as classes
import resources.lib.comm as comm
from resources.lib.upnext import upnext_signal

import xbmc

import xbmcaddon

import xbmcplugin


def play(url):
    try:
        addon = xbmcaddon.Addon()
        p = classes.Program()
        p.parse_kodi_url(url)
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

        listitem = comm.create_listitem(label=p.get_list_title(),
                                        iconImage=p.thumb,
                                        thumbnailImage=p.thumb,
                                        path=str(stream_url))
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

        listitem.setProperty('isPlayable', 'true')
        if utils.get_kodi_major_version() >= 18:
            listitem.setIsFolder(False)

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

        np = comm.get_next_program(p)
        if not isinstance(np, classes.Program):
            return

        next_info = OrderedDict(
            current_episode=OrderedDict(
                episodeid=p.id,
                tvshowid=p.get_tvshowid(),
                title=p.get_title(),
                art={
                    'thumb': p.get_thumb(),
                    'tvshow.fanart': p.get_fanart(),
                },
                season=p.get_season_no(),
                episode=p.get_episode_no(),
                showtitle=p.get_series_title(),
                plot=p.get_description(),
                playcount=0,
                rating=None,
                firstaired=p.get_date(),
                runtime=p.get_duration(),
            ),
            next_episode=OrderedDict(
                episodeid=np.id,
                tvshowid=np.get_tvshowid(),
                title=np.get_title(),
                art={
                    'thumb': np.get_thumb(),
                    'tvshow.fanart': np.get_fanart(),
                },
                season=np.get_season_no(),
                episode=np.get_episode_no(),
                showtitle=np.get_series_title(),
                plot=np.get_description(),
                playcount=0,
                rating=None,
                firstaired=np.get_date(),
                runtime=np.get_duration(),
            ),
            play_url='{0}?{1}'.format(sys.argv[0], np.make_kodi_url()),
            notification_offset=p.get_credits_time()
        )

        upnext_signal('plugin.video.sbs', next_info)

    except Exception:
        utils.handle_error("Unable to play video")
