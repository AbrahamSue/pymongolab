#!/usr/bin/env python

import urllib
import urllib2
import httplib2
import json
from datetime import tzinfo, timedelta, datetime

__Base_URL__ = 'https://api.mongolab.com/api/1'
#mu(){ echo "$MDBURLBase/${1:-databases}?apiKey=$MDBAPIKey"; }
__apis__ = {
    'list_databases': { 'Command': 'GET /databases' },
    'list_clusters' : { 'Command': 'GET /clusters/{cluster}/databases' },
    'list_collections': { 'Command': 'GET /databases/{database}/collections' },
    'list_documents': {	'Command': 'GET /databases/{database}/collections/{collection}', 
            'Param': '[q=<query>][&c=true][&f=<fields>][&fo=true][&s=<order>][&sk=<skip>][&l=<limit>]' },
    'insert_document': { 'Command': 'POST /databases/{database}/collections/{collection}', 'Return': 'json[_id][$oid]' },
    'update_documents': { 'Command': 'PUT /databases/{database}/collections/{collection}', 'Param': '[q=<query>][&m=true][&u=true]' },
    'get_document': { 'Command': 'GET /databases/{database}/collections/{collection}/{_id}'},
    'set_document': { 'Command': 'PUT /databases/{database}/collections/{collection}/{_id}'},
    'del_document': { 'Command': 'DELETE /databases/{database}/collections/{collection}/{_id}'},
    'run_command': { 'Command': 'POST /databases/{database}/runCommand'}
}

__headers__ = {
  'User-Agent' : 'Mozilla/5.0 (Windows; U; MSIE 9.0; WIndows NT 9.0; en-US)',
  'Content-Type' : 'application/json'
}


class MongoLabClient():
    def __urlfetch_httplib2__(self, url, method='GET', headers=None, data=None):
#        print "__urlfetch_httplib2__ called with\n  %s %s %s %s\n" % ( method, url, headers, data )
        return httplib2.Http(disable_ssl_certificate_validation=True).request(url, method, headers=headers, body=data)

    def __MongoLabAPI_Handler__(self, func, **kwargs):
    #    if func not in __apis__.keys():
    #        yield None
    #    print kwargs
        if func not in __apis__: return None
        fns = __apis__[ func ]
        if 'Command' not in fns: return None
        ( verb, cmd_uri ) = fns['Command'].split(' ', 2) 
        kw = self.kwdefault.copy()
        kw.update(kwargs)
        ps = ''
        if 'Param' in fns:
            pl = fns['Param'].replace('[','').split('&')
            plManda = [ x.split("=", 1)[0] for x in pl if ']' not in x ]
            plOptional = [ x.split("=", 1)[0] for x in pl if ']'  in x ]
            plMissing = filter(lambda x:x not in kw, plManda)
            plProvided = filter(lambda x:x in kw, plManda + plOptional)
            if len(plMissing) > 0: return None
            ps = '&' + '&'.join( [ '='.join( (x, urllib.quote_plus( str( kw[x] )) ) ) for x in plProvided ] )
    
        uri = "%s%s?apiKey=%s%s" % (__Base_URL__, cmd_uri.format(**kw), self.APIKey, ps)
#        print "Calling %s with %s: %s\n" % ( func, verb, uri)
        ds = json.dumps(
                 kw['data'], skipkeys=True, sort_keys=True, indent=4,
                 default=lambda x: x if isinstance(x, (str, unicode, int, long, float)) else "%s object at %s" % (type(x), hex(id(x))) 
             ) if 'data' in kw else None

#        data = kw['data'] if 'data' in kw else None
        try: resp, content = self.urlfetch(uri, verb, __headers__, ds)
        except httplib2.ServerNotFoundError as e:
            print '%s is not avaiable' % uri

#        print resp
#        print content
#        st = int(resp['status']) if 'status' in resp else 0
        contentjs=None
        if 'status' in resp and resp['status'].startswith('2') \
         and 'content-type' in resp and resp['content-type'].startswith('application/json'):
            contentjs = json.loads(content)
            if 'Return' in fns and fns['Return'].startswith('json'):
#                print __apis__[ func ]['Return']
#                print __apis__[ func ]['Return'].replace(']', '')
#                print __apis__[ func ]['Return'].replace(']', '').split('[')
                for k in __apis__[ func ]['Return'].replace(']', '').split('[')[1:]:
#                    print "k = %s" % k
                    if k not in contentjs: break
                    contentjs = contentjs[k]
        return contentjs

#        req = urllib2.Request(uri, None, __headers__)
#        try: response = urllib2.urlopen(req)
#        except URLError as e:
#            print e.reason
#        except HTTPError as e:
#            print 'The server couldn\'t fulfill the request.'
#            print 'Error code: ', e.code
    
        #print type(response)
        #js = response.read()
        #print js
        #print json.loads(js)
        return json.loads(response.read())

    def __make_method__(self, name):
        def __method__(self, **kwargs):
            return self.__MongoLabAPI_Handler__(name, **kwargs)
        return __method__

    def __init__(self, __api_key__):
        self.APIKey = __api_key__
        self.urlfetch = self.__urlfetch_httplib2__
        self.kwdefault = {}
#        print __api_key__
#        print len(__api_key__)
        if len(__api_key__) == 32:
            for name in __apis__:
                setattr( self.__class__, name, self.__make_method__(name))

    def set(self, **kwargs):
        self.kwdefault.update(kwargs)

if __name__ == "__main__":
    from os import environ
#    print __apis__
#    print environ['MANGOLAB_APIKEY']
    mc = MongoLabClient(environ['MANGOLAB_APIKEY'])
#    print dir(mc)
    #col = mc.list_collections(database='default')

#    for db in __MongoLabAPI_Handler__(mc, 'list_databases'):
#        print "Database: %s" % db
#        for col in __MongoLabAPI_Handler__(mc, 'list_collections', database=db):
#            print "    Collection: %s" % col
#            doc = __MongoLabAPI_Handler__(mc, 'list_documents', database=db, collection=col)
#            print "        %s" % doc

#    for db in mc.list_databases():
#        print "Database: %s" % db
#        for col in mc.list_collections(database=db):
#            print "    Collection: %s" % col
#            docs = mc.list_documents(database=db, collection=col)
#            print "        %s" % docs

#    for x in mc.list_documents(database='default', collection='Proxy'):
#        print mc.get_document(database='default', collection='Proxy', _id=x['_id']['$oid'])
#    for x in mc.list_documents(database='default', collection='Proxy'):
#        print mc.get_document(database='default', collection='Proxy', _id=x['_id']['$oid'])

#    print mc.insert_document(database='default', collection='test', data={ "name": "test", "value": "35499", "timestamp" : datetime.now().isoformat() })
#    print mc.del_document(database='default', collection='test', _id='56ba205be4b0a81ce4060509')
    mc.set(database='test', collection='Proxy')
    mc.set(database='test1l')
    mc.set(collection='Proxyi1')
    mc.set(database='default', collection='Proxy')
   
    print mc.list_documents()
    print mc.list_documents(collection='test', q=json.dumps({ "name": "test" }), c='true')
    print mc.run_command(database='default', data={ 'getLastError':'test' } )

#    __MongoLabAPI_Handler__(mc, 'list_databases')


