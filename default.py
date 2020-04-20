import os
import sys
import xbmcaddon
import xbmc
# fix for python bug
import _strptime  # noqa: F401

from aussieaddonscommon import utils

# Add our resources/lib to the python path
addon_dir = xbmcaddon.Addon().getAddonInfo('path')
sys.path.insert(0, os.path.join(addon_dir, 'resources', 'lib'))

import comm  # noqa: E402
import index  # noqa: E402
import play  # noqa: E402

# Print our platform/version debugging information
utils.log_kodi_platform_version()

if __name__ == "__main__":
    addon = xbmcaddon.Addon()
    if addon.getSetting('firstrun') == 'true':
        utils.dialog_message(
            'Welcome to the new On Demand add-on. An SBS On Demand account '
            'is now required to use this service. Please sign up at '
            'sbs.com.au or in the mobile app, then enter your details in '
            'the add-on settings.')
        comm.get_login_token()
        addon.setSetting('firstrun', 'false')
    params_str = sys.argv[2]
    params = utils.get_url(params_str)
    utils.log(params)
    if len(params) == 0:
        index.make_index_list()
    elif params.get('obj_type') == 'Program':
        play.play(params_str)
    elif 'feed_url' in params:
        index.make_entries_list(params)
    elif 'category' in params or params.get('item_type') in ['ProgramGenre', 'FilmGenre', 'Channel']:
        index.make_category_list(params)
    elif 'action' in params:
        if params['action'] == 'sendreport':
            utils.user_report()
        elif params['action'] == 'settings':
            xbmcaddon.Addon().openSettings()
        elif params['action'] == 'logout':
            comm.clear_login_token()
        elif params['action'] == 'login':
            comm.get_login_token()
            xbmc.executebuiltin('Container.Refresh')
