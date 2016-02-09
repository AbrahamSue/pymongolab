#!/usr/bin/env python

import urllib
import urllib2
import json

__Base_URL__ = 'https://api.mongolab.com/api/1'
#mu(){ echo "$MDBURLBase/${1:-databases}?apiKey=$MDBAPIKey"; }
__apis__ = {
    'list_databases': { 'Command': 'GET /databases' },
    'list_clusters' : { 'Command': 'GET /clusters/{cluster}/databases' },
    'list_collections': { 'Command': 'GET /databases/{database}/collections' },
    'list_documents': {	'Command': 'GET /databases/{database}/collections/{collection}', 
            'Param': '[q=<query>][&c=true][&f=<fields>][&fo=true][&s=<order>][&sk=<skip>][&l=<limit>]' },
    'insert_document': { 'Command': 'POST /databases/{database}/collections/{collection}' },
    'update_documents': { 'Command': 'PUT /databases/{database}/collections/{collection}', 'Param': '[q=<query>][&m=true][&u=true]' },
    'get_document': { 'Command': 'GET /databases/{database}/collections/{collection}/{_id}'},
    'set_document': { 'Command': 'PUT /databases/{database}/collections/{collection}/{_id}'},
    'del_document': { 'Command': 'DELETE /databases/{database}/collections/{collection}/{_id}'},
}

__headers__ = {
  'User-Agent' : 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US)',
  'Content-Type' : 'Application/json'
}

def __MongoLabAPI_Handler__(o, func, **kwargs):
#    if func not in __apis__.keys():
#        yield None
#    print kwargs
    ( verb, cmd_uri ) = __apis__[ func ]['Command'].split(' ', 2) 
    uri = "%s%s?apiKey=%s" % (__Base_URL__, cmd_uri.format(**kwargs), o.APIKey)
    print "Calling %s with %s: %s\n" % ( func, verb, uri)
    req = urllib2.Request(uri, None, __headers__)
    try: response = urllib2.urlopen(req)
    except URLError as e:
        print e.reason
    except HTTPError as e:
        print 'The server couldn\'t fulfill the request.'
        print 'Error code: ', e.code
    else:
        pass

    #print type(response)
    js = response.read()
    #print js
    #print json.loads(js)
    return json.loads(js)


def __make_method__(name):
    def __method__(self, **kwargs):
        __MongoLabAPI_Handler__(self, name, **kwargs)
    return __method__

class MongoLabClient():
    def __init__(self, __api_key__):
        self.APIKey = __api_key__
#        print __api_key__
#        print len(__api_key__)
        if len(__api_key__) == 32:
            for name in __apis__:
                setattr( self.__class__, name, __make_method__(name))

if __name__ == "__main__":
    from os import environ
#    print __apis__
#    print environ['MANGOLAB_APIKEY']
    mc = MongoLabClient(environ['MANGOLAB_APIKEY'])
#    print dir(mc)
    #col = mc.list_collections(database='default')
    for db in __MongoLabAPI_Handler__(mc, 'list_databases'):
        print "Database: %s" % db
        for col in __MongoLabAPI_Handler__(mc, 'list_collections', database=db):
            print "    Collection: %s" % col
            doc = __MongoLabAPI_Handler__(mc, 'list_documents', database=db, collection=col)
            print "        %s" % doc
#    mc.insert_document(database='default', collection='test', q='{ "name": "test" }')
#    __MongoLabAPI_Handler__(mc, 'list_databases')


