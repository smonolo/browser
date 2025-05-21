import os
from url import URL


def show(body: str):
  in_tag = False

  for c in body:
    if c == "<":
      in_tag = True
    elif c == ">":
      in_tag = False
    elif not in_tag:
      print(c, end="")

def load(url: URL):
  body = url.request()
  
  show(body)

if __name__ == "__main__":
  import sys

  if len(sys.argv) < 2:
    url = "file://" + os.path.abspath(sys.argv[0])
  else:
    url = sys.argv[1]

  load(URL(url))