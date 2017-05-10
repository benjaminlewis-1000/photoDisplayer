#! /usr/bin/env python

import sys
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
# import yaml
import xmltodict
# from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

def doit(json):

    with open('../config/params.xml') as stream:
        try:
            params = xmltodict.parse(stream.read())
        except Exception as exc:
            print(exc)
            exit(1)
    with open('received.out', 'w+') as f:
        print >>f, json


    # with open('../config/serverParams.yaml') as stream:
    #     try:
    #         params = yaml.load(stream)
    #     except yaml.YAMLError as exc:
    #         print(exc)
            # exit(0)

    proxy = xmlrpclib.ServerProxy("http://127.0.0.1:" + str(params['params']['serverParams']['displayServerPort']) + "/")

    try:
        print proxy.buildQuery(json);
        # exit(1)
    except xmlrpclib.Fault as err:
        print "A fault occurred"
        print "Fault code: %d" % err.faultCode
        print "Fault string: %s" % err.faultString
        # exit(0)


json = str(sys.argv[1])
with open('received.out', 'w+') as f:
    print >>f, json
# json = '''[{"\"criteriaType\"":"\"Date Range\"","\"booleanValue\"":"\"2017/05/01\"","\"criteriaVal\"":"\"<None>\""}]'''
doit(json)