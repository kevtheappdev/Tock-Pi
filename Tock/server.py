import json

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

from config import *

class ServerRequests(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        endpoint = self.parse_path()
        if not endpoint:
            self.wfile.write(bytes('{"status": "failed"}'.format(self.path), 'UTF-8'))
        else:
            endpoint()

    def connect_endpoint(self):
        config = Config('tock.config').to_dict()
        ret = {'current_config': config, 'status': 'ok'}
        json_repr = json.dumps(ret)
        self.wfile.write(bytes(json_repr, 'UTF-8'))

    def parse_path(self):
        # retreive endpoint function from url path
        path = self.path
        path_components = path.split('/')
        path_components = [path_comp for path_comp in path_components if path_comp]
        if len(path_components) > 1 or len(path_components) == 0:
            return None
        endpoint_name = path_components[0]
        print(endpoint_name)
        try:
            endpoint_func = getattr(self, '{}_endpoint'.format(endpoint_name))
        except AttributeError:
            # TODO: add logging at failure points
            return None
        else:
            return endpoint_func

def run(server_class=HTTPServer, handler_class=ServerRequests):
    server_address = ('', 80)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()
