import logging

from pyeta import VariableList, Variable, Eta

if __name__ == '__main__':
  # Set logging to debug is optional, but will show some behind-the-scene stuff
  logging.basicConfig()
  logging.getLogger("pyETA").setLevel("DEBUG")

  eta = Eta("heizung.speedport.ip")

  # Print available Nodes (the tab names on ETAtouch)
  nodes = eta.get_nodes()
  print("".join(f"{str(s)}, " for s in nodes))

  kessel_node: VariableList = nodes["Kessel"]
  zaelerstaende: VariableList = kessel_node.elements["Zählerstände"]
  volllaststunden: Variable = zaelerstaende.elements["Volllaststunden"]
  gesamtverbrauch: Variable = zaelerstaende.elements["Gesamtverbrauch"]

  print(f"Without update (Volllaststunden): {volllaststunden.value} (Updated: {volllaststunden.last_updated})")

  # Update only one variable state
  eta.update_eta_object(volllaststunden)
  print(f"With single update (Volllaststunden): {volllaststunden.value} (Updated: {volllaststunden.last_updated})")

  # Update serveral variables states at once
  eta.update_eta_object(zaelerstaende)
  print(f"With group update (Volllaststunden): {volllaststunden.value} (Updated: {volllaststunden.last_updated})")
  print(f"With group update (Gesamtverbrauch): {gesamtverbrauch.value} (Updated: {gesamtverbrauch.last_updated})")
