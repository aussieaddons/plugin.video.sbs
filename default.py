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

import os, sys

# Add our resources/lib to the python path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except:
    current_dir = os.getcwd()

sys.path.append(os.path.join(current_dir, 'resources', 'lib'))
import config, utils, index, categories, section, entries, play

# Print our platform/version debugging information
utils.log_xbmc_platform_version()

if __name__ == "__main__" :
    params_str = sys.argv[2]
    params = utils.get_url(params_str)
    utils.log("Loading add-on with params: %s" % params)

    if (len(params) == 0):
        index.make_index_list()
    elif params.has_key('play'):
        play.play(params_str)
    elif params.has_key('entries_url'):
        entries.make_entries_list(params_str)
    elif params.has_key('section'):
        section.make_section_list(params_str)
    elif params.has_key('category'):
        categories.make_category_list(params_str)
