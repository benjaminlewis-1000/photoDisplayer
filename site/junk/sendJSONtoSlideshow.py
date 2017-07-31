#! /usr/bin/env python

import sys
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
import json
import xmltodict
# from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

def doit(json):

    errors = []
    debugs = []
    errDict = {}

    debugs.append(json)

    with open('../../config/params.xml') as stream:
        try:
            params = xmltodict.parse(stream.read())
            debugs.append('Params opened OK')
        except Exception as exc:
            errors.append(exc)
            errDict['errors'] = errors
            errDict['debug'] = debugs
            return json.dumps(errDict)
#    with open('received.out', 'w+') as f:
#        print >>f, json
#    print params['params']['serverParams']['displayServerPort']

    try:
        proxy = xmlrpclib.ServerProxy("http://127.0.0.1:" + str(params['params']['serverParams']['displayServerPort']) + "/")
        debugs.append('XML Server opened OK')
    except Exception as exc:
        errors.append(exc)
        errDict['errors'] = errors
        errDict['debug'] = debugs
        return json.dumps(errDict)

    # print json
    try:
        errDict['errors'] = errors
        errDict['debug'] = debugs
        return errDict
        debugs.append(proxy.buildQuery(json))
        debugs.append('Query sent to server and processed OK')
        # exit(1)
    except xmlrpclib.Fault as err:
        errors.append("A fault occurred")
        errors.append("Fault code: %d" % err.faultCode)
        errors.append("Fault string: %s" % err.faultString)
        # exit(0)


    errDict['errors'] = errors
    errDict['debug'] = debugs
    return json.dumps(errDict)


json = str(sys.argv[1])
#with open('received.out', 'w+') as f:
 #   print >>f, json
#json = '''[{"criteriaType":"Person","booleanValue":"is","criteriaVal":"Adam Lewis"}]'''
# print json
print doit(json)
