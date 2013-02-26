#! /usr/bin/env python
#
# Mixpanel, Inc. -- http://mixpanel.com/
#
# Python API client library to consume mixpanel.com analytics data.

import hashlib
import urllib
import time
import subprocess
import base64
from datetime import datetime
import random
try:
    import json
except ImportError:
    import simplejson as json

class Mixpanel(object):

    ENDPOINT = 'http://mixpanel.com/api'
    VERSION = '2.0'

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        
    def request(self, methods, params, format='json'):
        """
            methods - List of methods to be joined, e.g. ['events', 'properties', 'values']
                      will give us http://mixpanel.com/api/2.0/events/properties/values/
            params - Extra parameters associated with method
        """
        params['api_key'] = self.api_key
        params['expire'] = int(time.time()) + 600   # Grant this request 10 minutes.
        params['format'] = format
        if 'sig' in params: del params['sig']
        params['sig'] = self.hash_args(params)

        request_url = '/'.join([self.ENDPOINT, str(self.VERSION)] + methods) + '/?' + self.unicode_urlencode(params)

        request = urllib.urlopen(request_url)
        data = request.read()

        return json.loads(data)

    def unicode_urlencode(self, params):
        """
            Convert lists to JSON encoded strings, and correctly handle any 
            unicode URL parameters.
        """
        if isinstance(params, dict):
            params = params.items()
        for i, param in enumerate(params):
            if isinstance(param[1], list): 
                params[i] = (param[0], json.dumps(param[1]),)

        return urllib.urlencode(
            [(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params]
        )

    def hash_args(self, args, secret=None):
        """
            Hashes arguments by joining key=value pairs, appending a secret, and 
            then taking the MD5 hex digest.
        """
        for a in args:
            if isinstance(args[a], list): args[a] = json.dumps(args[a])

        args_joined = ''
        for a in sorted(args.keys()):
            if isinstance(a, unicode):
                args_joined += a.encode('utf-8')
            else:
                args_joined += str(a)

            args_joined += '='

            if isinstance(args[a], unicode):
                args_joined += args[a].encode('utf-8')
            else:
                args_joined += str(args[a])

        hash = hashlib.md5(args_joined)

        if secret:
            hash.update(secret)
        elif self.api_secret:
            hash.update(self.api_secret)
        return hash.hexdigest() 


def track(event, properties=None):
    """ A simple function for asynchronously logging to the mixpanel.com API.
	This function requires `curl` and Python version 2.4 or higher.
	@param event: The overall event/category you would like to log this data under
	@param properties: A dictionary of key-value pairs that describe the event
	See http://mixpanel.com/api/ for further detail.
	@return Instance of L{subprocess.Popen}
    """
    if properties == None:
       properties = {}
    
    if "distinct_id" not in properties:
	properties['distinct_id'] =  datetime.utcnow().strftime("%S-%M-%H-%d-%b-%Y") + str(random.random())

    params = {"event": event, "properties": properties}
    data = base64.b64encode(json.dumps(params))
    request = "http://api.mixpanel.com/track/?data=" + data
    return subprocess.Popen(("curl",request), stderr=subprocess.PIPE, stdout=subprocess.PIPE)

# Example usage:
if __name__ == '__main__':
    #api = Mixpanel(
        #api_key = 'YOUR KEY', 
        #api_secret = 'YOUR SECRET'
    #)
    #data = api.request(['events'], {
        #'event' : ['pages',],
        #'unit' : 'hour',
        #'interval' : 24,
        #'type': 'general'
    #})
    #print data
    track("invite-friends", {"method": "email", "number-friends": "12", "ip": "123.123.123.123"})
