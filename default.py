import sys

# fix for python bug
import _strptime  # noqa: F401

from aussieaddonscommon import utils

from resources.lib import comm
from resources.lib import index
from resources.lib import play
from resources.lib import search

import xbmc

import xbmcaddon

# Print our platform/version debugging information
utils.log_kodi_platform_version()


def main():
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
    elif 'category' in params or params.get(
            'item_type') in ['ProgramGenre', 'FilmGenre', 'Channel']:
        if params.get('category') == 'Search':
            index.make_search_history_list()
        else:
            index.make_category_list(params)
    elif 'action' in params:
        action = params.get('action')
        if action == 'favouritescategories':
            index.make_favourites_categories_list()
        elif action == 'addfavourites':
            comm.add_to_favourites(params)
        elif action == 'removefavourites':
            comm.remove_from_favourites(params)
            xbmc.executebuiltin('Container.Refresh')
        elif action == 'searchhistory':
            if params.get('name') == 'New Search':
                search.get_search_input()
            else:
                index.make_search_list(params)
        elif action == 'removesearch':
            search.remove_from_search_history(params.get('name'))
        elif action == 'sendreport':
            utils.user_report()
        elif action == 'settings':
            xbmcaddon.Addon().openSettings()
        elif action == 'logout':
            comm.clear_login_token()
        elif action == 'login':
            comm.get_login_token()
            xbmc.executebuiltin('Container.Refresh')


if __name__ == "__main__":
    main()
