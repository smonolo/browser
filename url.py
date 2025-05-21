import socket
import ssl


port_schemes = ["http", "https"]

def get_scheme_and_url(url: str):
    colon_schemes = ["data", "view-source"]
    sep = ":" if any(url.startswith(scheme + ":") for scheme in colon_schemes) else "://"
    scheme, url = url.split(sep, 1)

    assert scheme in [*port_schemes, "file", *colon_schemes]

    return scheme, url

def get_port_from_scheme(scheme: str):
    ports = {
        "http": 80,
        "https": 443,
    }

    return ports[scheme]

class URL:
    def __init__(self, url: str):
        self.socket = None
        self.scheme, url = get_scheme_and_url(url)
        self.view_source = False

        if self.scheme == "view-source":
            self.scheme, url = get_scheme_and_url(url)
            self.view_source = True

        if self.scheme == "file":
            self.path = url
            return
        
        if self.scheme == "data":
            self.path = url.split(",", 1)[1]
            return

        if self.scheme in port_schemes:
            self.port = get_port_from_scheme(self.scheme)

        if "/" not in url:
            url = url + "/"
          
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def request(self):
        if self.scheme == "file":
            return open(self.path, "r").read()
        
        if self.scheme == "data":
            return self.path

        if self.socket:
            s = self.socket
        else:
            s = socket.socket()
            s.connect((self.host, self.port))

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)

        request = "GET {} HTTP/1.0\r\n".format(self.path)
        request_headers = {
            "host": self.host,
            "connection": "keep-alive",
            "user-agent": "smonolo-browser",
        }

        for key, value in request_headers.items():
            request += "{}: {}\r\n".format(key, value)

        request += "\r\n"

        s.send(request.encode("utf8"))

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}

        while True:
            line = response.readline()
            
            if line == "\r\n": break

            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content_length = response_headers["content-length"]

        if content_length:
            content = response.read(int(content_length))
        else:
            content = response.read()

        self.socket = s

        if self.view_source:
            content = content.replace("<", "&lt;").replace(">", "&gt;")

        return content
