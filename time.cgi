#!/usr/local/bin/python3
from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("Content-Type: text/html; charset=utf-8")
print()
print(f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Server Time</title>
  </head>
  <body>
    <h1>Server Time</h1>
    <p>{now}</p>
  </body>
</html>""")
