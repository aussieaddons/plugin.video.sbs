# flake8: noqa

CONFIG_URL = 'https://www.sbs.com.au/api/v3/video_config?context=android&device=phone&version=3.2.1'
STREAM_URL = 'https://www.sbs.com.au/api/v3/video_stream?id={VIDEOID}&context=android&device=phone&version=3.2.1&uniqueid={UNIQUEID}&deviceadid={AAID}&deviceadidoptout={OPTOUT}&cxid=[CXID]'
LOGIN1_URL = 'https://www.sbs.com.au/api/v3/janrain/auth_native_traditional'
LOGIN2_URL = 'https://www.sbs.com.au/api/v3/member/completelogin?context=android&device=phone&version=3.2.1&loginVersion=1.0.0&auth_token={token}'
SERIES_URL = 'https://www.sbs.com.au/api/v3/video_program?id=[SERIESID]&context=android&device=phone&version=3.2.1'
EPISODE_URL = 'https://www.sbs.com.au/api/v3/video_search/?filters={{pilatDealcode}}{{{pilatDealcode}}},{{season}}{{{season}}},{{episodeNumber}}{{{episodeNumber}}}&context=android&device=phone&version=3.2.1'

FAV_DICT = {
    'TVSeries': 'Program',
    'Movie': 'Movie',
    'OneOff': 'Movie'
}