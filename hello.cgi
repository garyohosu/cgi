#!/usr/local/bin/python3
import sys

print("Content-Type: text/html; charset=utf-8")
print()
print("""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Hello CGI</title>
  </head>
  <body>
    <h1>Hello CGI</h1>
    <p>Python version: {}</p>
  </body>
</html>""".format(sys.version.split()[0]))
