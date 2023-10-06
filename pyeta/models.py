import datetime
from enum import StrEnum, auto
from typing import Self


class EtaObject:
  name: str
  uri: str

  def __init__(self, name: str, uri: str):
    self.name = name
    self.uri = uri

  def __str__(self) -> str:
    return f"{self.name} ({self.uri})"


class VariableType(StrEnum):
  DEFAULT = auto()
  TEXT = auto()
  TIMESLOT = auto()


class Variable(EtaObject):
  adv_text_offset: int
  unit: str
  str_value: str
  scale_factor: int
  dec_places: int
  value: int
  variable_type: VariableType
  writeable: bool

  def __init__(self,
               name: str,
               uri: str,
               variable_type: VariableType = None,
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
    self.variable_type = variable_type

    if value is not None and str_value is not None:
      self.last_updated = datetime.datetime.now()
    else:
      self.last_updated = None

  def __str__(self) -> str:
    return (f"{self.name} ({self.uri}): {self.value} (strValue='{self.str_value}', type={self.variable_type}"
            f" unit={self.unit}, scaleFactor={self.scale_factor}, decPlaces={self.dec_places}, advTextOffset={self.adv_text_offset},"
            f" last_updated={self.last_updated})")

  def normalized_value(self) -> float | None:
    """
    Apply scale factor to value.
    :return: The normalized value after applying the scale factor. Or None in case there is no value.
    """
    if self.value is not None:
      return self.value / max(self.scale_factor, 1)
    else:
      return None


class VariableList(EtaObject):
  elements: dict[str, Variable | Self]

  def __init__(self, name: str, uri: str, elements: dict[str, Variable | Self]):
    super().__init__(name, uri)
    self.elements = elements

  def __str__(self) -> str:
    return f"{self.name} ({self.uri}) {self.elements}"
