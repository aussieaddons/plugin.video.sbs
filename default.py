#
#  SBS On Demand Kodi Add-on
#  Copyright (C) 2015 Andy Botting
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import xbmcaddon
# fix for python bug
import _strptime  # noqa: F401

from aussieaddonscommon import utils

# Add our resources/lib to the python path
addon_dir = xbmcaddon.Addon().getAddonInfo('path')
sys.path.insert(0, os.path.join(addon_dir, 'resources', 'lib'))

import categories  # noqa: E402
import entries  # noqa: E402
import index  # noqa: E402
import play  # noqa: E402
import section  # noqa: E402

# Print our platform/version debugging information
utils.log_kodi_platform_version()

if __name__ == "__main__":
    params_str = sys.argv[2]
    params = utils.get_url(params_str)

    if len(params) == 0:
        index.make_index_list()
    elif 'play' in params:
        play.play(params_str)
    elif 'entries_url' in params:
        entries.make_entries_list(params_str)
    elif 'section' in params:
        section.make_section_list(params_str)
    elif 'category' in params:
        categories.make_category_list(params_str)
    elif 'action' in params:
        if params['action'] == 'sendreport':
            utils.user_report()
        elif params['action'] == 'settings':
            xbmcaddon.Addon().openSettings()
