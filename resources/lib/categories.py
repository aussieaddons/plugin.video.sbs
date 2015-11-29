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
import comm
import utils
import xbmc
import xbmcgui
import xbmcplugin

def make_category_list(url):
    utils.log("Making category list")
    try:
        params = utils.get_url(url)
        categories = comm.get_category(params['category'])

        ok = True
        for c in categories.get('children', []):
            if 'children' in c:
                url = "%s?%s" % (sys.argv[0], utils.make_url({
                                 'category': params['category'],
                                 'section': c['name']}))
            elif 'url' in c:
                url = "%s?%s" % (sys.argv[0], utils.make_url({
                                 'entries_url': c['url']}))
            else:
                #utils.log("Skip category due to no entries or url: %s" % c)
                continue

            thumbnail = c.get('thumbnail', None)
            listitem = xbmcgui.ListItem(label=c['name'], iconImage=thumbnail,
                                        thumbnailImage=thumbnail)
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url,
                                             listitem=listitem, isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except:
        utils.handle_error()
