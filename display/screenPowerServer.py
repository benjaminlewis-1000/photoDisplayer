#! /usr/bin/env python

import screen_manager as sm

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/',)

# Create server

class screenPowerServer:

    def __init__(self, xmlParams):

        self.server = SimpleXMLRPCServer(("127.0.0.1", 8338),
                                    requestHandler=RequestHandler)
                                    
        self.screenManager = sm.tvStateManager()
        
    def run(self):
        self.server.register_function(self.startSlideshow, 'startSlideshow')
        self.server.register_function(self.setSlideshowProperties, 'setSlideshowProperties')
        self.server.register_function(self.buildQuery, 'buildQuery')
        self.server.register_function(self.loadSavedShow, 'loadSavedShow')
        self.server.register_function(self.endSlideshow, 'endSlideshow')
        self.server.register_function(self.getShowRunningState, 'getShowRunningState')
        self.server.serve_forever()