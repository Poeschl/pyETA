import logging

import pyETA

if __name__ == '__main__':
  # Set logging to debug is optional, but will show some behind-the-scene stuff
  logging.basicConfig()
  logging.getLogger("pyETA").setLevel("DEBUG")

  eta = pyETA.Eta("heizung.speedport.ip")
  nodes = eta.get_nodes()

  # Print available Nodes (the tab names on ETAtouch)
  print("".join(f"{str(s)}, " for s in nodes))
