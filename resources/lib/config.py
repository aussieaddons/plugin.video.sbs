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

import os
import version

NAME = 'SBS On Demand'
ADDON_ID = 'plugin.video.sbs'
VERSION = version.VERSION

GITHUB_API_URL = 'https://api.github.com/repos/xbmc-catchuptv-au/plugin.video.sbs'
ISSUE_API_URL = GITHUB_API_URL + '/issues'
ISSUE_API_AUTH = 'eGJtY2JvdDo1OTQxNTJjMTBhZGFiNGRlN2M0YWZkZDYwZGQ5NDFkNWY4YmIzOGFj'
GIST_API_URL = 'https://api.github.com/gists'

# os.uname() is not available on Windows, so we make this optional.
try:
    uname = os.uname()
    os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
    os_string = ''

user_agent = '%s add-on for Kodi/XBMC %s%s' % (NAME, VERSION, os_string)

config_url = 'http://www.sbs.com.au/api/video_config/?context=android&form=json'
index_url = 'http://www.sbs.com.au/api/video_menu/?group=41&context=android&form=json'
token_url = 'https://secure.sbs.com.au/api/member/sessiontoken?context=android&form=json'
stream_url = 'http://www.sbs.com.au/api/video_feed/smil?context=android&form=xml&id=%s'
subtitle_url = 'http://videocdn.sbs.com.au/u/video/SBS/managed/closedcaptions/'

# Used for basic auth when fetching stream information
auth_string = 'YW5kcm9pZDg5YWQ1NWU5ZjljZjNjMWJiYzUyMTA2ZTNiMzkwMmQ1OTk1MjEwYjU6YW5kcm9pZA=='
