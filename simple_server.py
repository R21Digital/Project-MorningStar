#!/usr/bin/env python3
"""
Simple HTTP server to serve SWGDB static files on localhost:8000
"""
import http.server
import socketserver
import os
from pathlib import Path

# Set the port
PORT = 8080

# Change to the swgdb_site directory which contains the HTML files
os.chdir('swgdb_site')

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

# Create the server
with socketserver.TCPServer(("127.0.0.1", PORT), CustomHTTPRequestHandler) as httpd:
    print(f"SWGDB Server running at http://localhost:{PORT}/")
    print("Visit http://localhost:8080/ to access SWGDB")
    print("Press Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")