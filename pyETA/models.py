import datetime


class EtaObject:

  def __init__(self, name: str, uri: str):
    self.name = name
    self.uri = uri

  def __str__(self) -> str:
    return f"{self.name} ({self.uri})"


class VariableList(EtaObject):

  def __init__(self, name: str, uri: str, elements: dict[str, EtaObject]):
    super().__init__(name, uri)
    self.elements = elements

  def __str__(self) -> str:
    return f"{self.name} ({self.uri}) {self.elements}"


class Variable(EtaObject):

  def __init__(self,
               name: str,
               uri: str,
               adv_text_offset: int = 0,
               unit: str = "",
               str_value: str = None,
               scale_factor: int = 1,
               dec_places: int = 0,
               value: int = None):
    super().__init__(name, uri)
    self.adv_text_offset = adv_text_offset
    self.unit = unit
    self.str_value = str_value
    self.scale_factor = scale_factor
    self.dec_places = dec_places
    self.value = value

    if value is not None and str_value is not None:
      self.last_updated = datetime.datetime.now()
    else:
      self.last_updated = None

  def __str__(self) -> str:
    return f"{self.name} ({self.uri}): {self.value} (strValue='{self.str_value}', unit={self.unit}, scaleFactor={self.scale_factor}, last_updated={self.last_updated})"


class Node(EtaObject):

  def __init__(self, name: str, uri: str, elements: dict[str, EtaObject]):
    super().__init__(name, uri)
    self.elements = elements

  def __str__(self) -> str:
    return f"{self.name} ({self.uri}) {self.elements}"
