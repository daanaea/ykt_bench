#!/usr/bin/env python3
import http.server
import json
import csv
import os

PORT = 8080
CSV_FILE = 'bank.csv'

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            file_exists = os.path.exists(CSV_FILE)

            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                if not file_exists:
                    writer.writerow(['timestamp', 'model_output', 'corrected_version', 'annotations'])

                writer.writerow([
                    data['timestamp'],
                    data['modelOutput'],
                    data['correctedVersion'],
                    json.dumps(data['annotations'], ensure_ascii=False)
                ])

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    print(f'Server running at http://localhost:{PORT}')
    http.server.HTTPServer(('', PORT), Handler).serve_forever()
