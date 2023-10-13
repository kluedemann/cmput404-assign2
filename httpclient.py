#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# Copyright 2023 Kai Luedemann
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPRequest:
    """Represent an HTTP request
    
    Params:
        method - the HTTP method string (e.g. 'GET', 'POST', etc)
        headers - a dict containing the headers to include in the request
        path - the path to request
        content - the string body to include with the request
    """

    def __init__(self, method="GET", headers={}, path="/", content="") -> None:
        self.method = method
        self.headers = headers
        self.path = path
        self.content = content

    def build(self):
        """Return the request as a string."""
        req = f"{self.method} {self.path} HTTP/1.1\r\n"
        for k, v in self.headers.items():
            req += f"{k}: {v}\r\n"
        req += "\r\n"
        return req + str(self.content)

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self):
        return f"Status code: {self.code}\n\n{self.body}"

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        """Return the HTTP status code received.
        
        Params:
            data - the HTTP reponse string received
        """
        try:
            return int(data.splitlines()[0].split()[1])
        except:
            # Invalid response: Could throw error
            return None

    def get_headers(self,data):
        """Create the headers to include with the HTTP request.
        
        Params:
            data - the content string to send with the request
        """
        headers = {}
        headers["Connection"] = "close"
        headers["Content-Length"] = len(data.encode('utf-8'))
        if data:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return headers

    def get_body(self, data):
        """Return the body of the HTTP response.
        
        Params:
            data - the HTTP response string received
        """
        ind = data.find("\r\n\r\n")
        if ind != -1:
            return data[ind + 4:]
        return ""
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def get_content(self, form_data):
        """Create the content string from the arguments.
        
        Params:
            form_data - the dict to encode using x-www-form-urlencoding
        """
        if form_data is not None:
            return urllib.parse.urlencode(form_data)
        return ""
    
    def get_path(self, parsed):
        """Return the path to request.
        
        Params:
            parsed - urllib.parse.ParseResult of the URL string
        """
        path = "/"
        if parsed.path != "":
            path = parsed.path
        if parsed.query != "":
            path += "?" + parsed.query
        return path

    
    def get_addr(self, parsed):
        """Return the host and port from the parsed URL.
        
        Params:
            parsed - urllib.parse.ParseResult of the URL string
        """
        parts = parsed.netloc.split(":")
        host = parts[0]
        if len(parts) > 1:
            port = int(parts[1])
        else:
            port = 80
        return host, port

    def GET(self, url, args=None):
        # Connect to socket
        parsed = urllib.parse.urlparse(url)
        host, port = self.get_addr(parsed)
        self.connect(host, port)

        # Create request
        path = self.get_path(parsed)
        content = self.get_content(args)
        headers = self.get_headers(content)
        headers["Host"] = parsed.netloc
        req = HTTPRequest("GET", headers, path, content)

        # Get response
        self.sendall(req.build())
        resp = self.recvall(self.socket)
        self.close()

        # Parse response
        code = self.get_code(resp)
        body = self.get_body(resp)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Connect to socket
        parsed = urllib.parse.urlparse(url)
        host, port = self.get_addr(parsed)
        self.connect(host, port)

        # Create request
        path = self.get_path(parsed)
        content = self.get_content(args)
        headers = self.get_headers(content)
        headers["Host"] = parsed.netloc
        req = HTTPRequest("POST", headers, path, content)
        
        # Get response
        self.sendall(req.build())
        resp = self.recvall(self.socket)
        self.close()

        # Parse response
        code = self.get_code(resp)
        body = self.get_body(resp)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
