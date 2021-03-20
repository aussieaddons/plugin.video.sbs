# flake8: noqa

APP_VERSION = '3.4.6'

CONFIG_URL = 'https://www.sbs.com.au/api/v3/video_config?context=android&device=phone&version=' + APP_VERSION
STREAM_URL = 'https://www.sbs.com.au/api/v3/video_stream?id={VIDEOID}&context=android&device=phone&version=' + APP_VERSION + '&uniqueid={UNIQUEID}&deviceadid={AAID}&deviceadidoptout={OPTOUT}&cxid=[CXID]'
LOGIN1_URL = 'https://www.sbs.com.au/api/v3/janrain/auth_native_traditional'
LOGIN2_URL = 'https://www.sbs.com.au/api/v3/member/completelogin?context=android&device=phone&version=' + APP_VERSION + '&loginVersion=1.0.0&auth_token={token}'
SERIES_URL = 'https://www.sbs.com.au/api/v3/video_program?id=[SERIESID]&context=android&device=phone&version=' + APP_VERSION
EPISODE_URL = 'https://www.sbs.com.au/api/v3/video_search/?filters={{pilatDealcode}}{{{pilatDealcode}}},{{season}}{{{season}}},{{episodeNumber}}{{{episodeNumber}}}&context=android&device=phone&version=' + APP_VERSION
DAI_URL = 'http://pubads.g.doubleclick.net/ondemand/hls/content/2488267/vid/{vid}/streams'

FAV_DICT = {
    'TVSeries': 'Program',
    'Movie': 'Movie',
    'OneOff': 'Movie'
}
