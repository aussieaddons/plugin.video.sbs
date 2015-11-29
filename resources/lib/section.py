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
import os
import urllib2
import urllib
import comm
import utils
import xbmc, xbmcgui, xbmcplugin

def make_section_list(url):
    utils.log("Making section list")
    try:
        params = utils.get_url(url)
        section = comm.get_section(params['category'], params['section'])

        ok = True

        if 'children' in section:
            for s in section['children']:
                # We override the A-Z list with a better layout
                if s['name'] == 'Programs A-Z':
                    url = "%s?%s" % (sys.argv[0], utils.make_url({'category': s['name']}))
                else:
                    url = "%s?%s" % (sys.argv[0], utils.make_url({'entries_url': s['url']}))
                listitem = xbmcgui.ListItem(s['name'])
                # Add the program item to the list
                ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except:
        utils.handle_error()
