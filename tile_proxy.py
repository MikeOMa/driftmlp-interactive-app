"""Small fixed-upstream proxy for CARTO raster tiles."""

import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TILE_PATH = re.compile(r"^/tiles/(\d{1,2})/(\d{1,10})/(\d{1,10})\.png$")
UPSTREAM = "https://basemaps.cartocdn.com/rastertiles/light_all/{z}/{x}/{y}.png"


class TileProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        match = TILE_PATH.fullmatch(self.path)
        if not match:
            self.send_error(404)
            return

        z, x, y = map(int, match.groups())
        if z > 20 or x >= 2**z or y >= 2**z:
            self.send_error(404)
            return

        token = os.environ.get("CARTO_TOKEN")
        if not token:
            self.send_error(503, "Map tiles are not configured")
            return

        url = UPSTREAM.format(z=z, x=x, y=y) + "?" + urlencode({"key": token})
        try:
            with urlopen(Request(url, headers={"User-Agent": "DriftMLP map tile proxy"}), timeout=15) as response:
                data = response.read()
                content_type = response.headers.get("Content-Type", "image/png")
                status = response.status
        except HTTPError as error:
            data = error.read()
            content_type = error.headers.get("Content-Type", "text/plain")
            status = error.code
        except (TimeoutError, URLError):
            self.send_error(502, "Tile provider unavailable")
            return

        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "public, max-age=86400")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        # Tile request paths are high volume; avoid adding them to container logs.
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8081), TileProxyHandler).serve_forever()
