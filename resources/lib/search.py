import json

import xbmc

import xbmcaddon

import xbmcgui

addon = xbmcaddon.Addon()


def get_search_history():
    search_history = addon.getSetting('SEARCH_HISTORY')
    if search_history == '':
        addon.setSetting('SEARCH_HISTORY', json.dumps([]))
        return []
    json_data = json.loads(search_history)
    return json_data


def get_search_input():
    search_string = xbmcgui.Dialog().input('Enter search terms')
    if not search_string:
        return
    add_to_search_history(search_string)
    import resources.lib.index as index
    index.make_search_list({'name': search_string})


def set_search_history(json_data):
    addon.setSetting('SEARCH_HISTORY', json.dumps(json_data))


def get_search_history_listing():
    listing = ['New Search']
    search_history = get_search_history()
    for item in search_history:
        listing.append(item)
    return listing


def add_to_search_history(search_string):
    search_history = get_search_history()
    if search_string not in search_history:
        search_history.append(search_string)
        set_search_history(search_history)


def remove_from_search_history(search_string):
    search_history = get_search_history()
    if search_string in search_history:
        search_history.remove(search_string)
        set_search_history(search_history)
    xbmc.executebuiltin('Container.Refresh')
