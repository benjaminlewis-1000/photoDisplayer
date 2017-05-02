#! /usr/bin/env python

import sys
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer
import yaml
# from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

def doit(json):


    with open('../config/serverParams.yaml') as stream:
        try:
            params = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            # exit(0)


    proxy = xmlrpclib.ServerProxy("http://127.0.0.1:" + str(params['displayServerPort']) + "/")

    try:
        print proxy.startSlideshow(json);
        # exit(1)
    except xmlrpclib.Fault as err:
        print "A fault occurred"
        print "Fault code: %d" % err.faultCode
        print "Fault string: %s" % err.faultString
        # exit(0)


json = sys.argv[1]
doit(json)