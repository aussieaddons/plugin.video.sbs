import xbmc
from json import dumps, loads
from base64 import b64encode

def upnext_signal(sender, next_info):
    """Send a signal to Kodi using JSON RPC"""
    data = [to_unicode(b64encode(dumps(next_info).encode()))]
    notify(sender=sender + '.SIGNAL', message='upnext_data', data=data)

def notify(sender, message, data):
    """Send a notification to Kodi using JSON RPC"""
    result = jsonrpc(method='JSONRPC.NotifyAll', params=dict(
        sender=sender,
        message=message,
        data=data,
    ))
    if result.get('result') != 'OK':
        xbmc.log('Failed to send notification: '
                    + result.get('error').get('message'))
        return False
    return True

def jsonrpc(**kwargs):
    """Perform JSONRPC calls"""
    if kwargs.get('id') is None:
        kwargs.update(id=0)
    if kwargs.get('jsonrpc') is None:
        kwargs.update(jsonrpc='2.0')
    return loads(xbmc.executeJSONRPC(dumps(kwargs)))

def to_unicode(text, encoding='utf-8', errors='strict'):
    """Force text to unicode"""
    if isinstance(text, bytes):
        return text.decode(encoding, errors=errors)
    return text
