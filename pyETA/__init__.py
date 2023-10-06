import datetime
import logging
import re
from xml.etree.ElementTree import XML, Element

from requests import get

from models import VariableList, Variable, VariableType

SUPPORTED_API_VERSIONS = ["1.2", "1.1", "1.0"]
API_VERSION_PATH = "/user/api"
MENU_PATH = "/user/menu"
VARIABLE_PATH = "/user/var"

TIMESLOT_REGEX_PATTERN = "\\d{2}:\\d{2} - \\d{2}:\\d{2} \\d{1,3}"

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


class Eta:
  """
  Represents a connection to you ETA heating system, further communication is done with methods of this class.

  :param host: The dns name or ip of your ETA heating system. Make sure to meet the precondition described in the package README.
  :param hide_io_variables: When enabled, all io interface variables are not included in the api requests. (Defaults to `True`)
  """

  def __init__(self, host: str, hide_io_variables: bool = True):
    self.url = "http://{0}:8080".format(host)
    self.hide_io_variables = hide_io_variables
    self.__check_compatibility()
    logger.info("Initialized ETAtouch REST connection to %s", host)

  def __check_compatibility(self):
    xml = self.__get_version_xml()

    api_element = xml[0]
    if not (api_element.tag.endswith("api") and api_element.attrib["version"] in SUPPORTED_API_VERSIONS):
      logger.error("Error: Not supported api version. Your ETAtouch REST api version is not supported by this library.")
      logger.error("Detected api version: '%s' Supported versions: %s", api_element.attrib["version"], SUPPORTED_API_VERSIONS)
      exit(1)
    logger.info("Detected ETAtouch REST api version: %s", api_element.attrib["version"])

  def get_nodes(self) -> dict[str, VariableList]:
    """
    Retrieves all available device nodes of you ETA heating system.
    The nodes are not filled with data but represent the structure of the available variables.
    :return: A dict with names of the nodes and a node object with nested variables.
    """
    xml = self.__get_menu_xml()
    nodes: dict[str, VariableList] = {}

    node: Element
    for node in xml[0]:
      node_elements = self.__parse_object_list(node)

      nodes[node.attrib["name"]] = VariableList(node.attrib["name"], node.attrib["uri"], node_elements)

    return nodes

  def __parse_object_list(self, root: Element) -> dict[str, Variable | VariableList]:
    elements: dict[str, Variable | VariableList] = {}
    node_object: Element

    uid_blacklist_regexes: list[str] = []

    if self.hide_io_variables:
      uid_blacklist_regexes.append(".*0/0/10...$")

    for node_object in root:

      if len(uid_blacklist_regexes) > 0:
        on_blacklist = False
        for regex in uid_blacklist_regexes:
          if re.search(regex, node_object.attrib["uri"]) is not None:
            on_blacklist = True
            break

        if on_blacklist:
          logger.debug("Skip %s (%s) since on blacklist", node_object.attrib["name"], node_object.attrib["uri"])
          continue

      if len(node_object) > 1:
        elements[node_object.attrib["name"]] = (VariableList(node_object.attrib["name"], node_object.attrib["uri"], self.__parse_object_list(node_object)))
      else:
        elements[node_object.attrib["name"]] = Variable(node_object.attrib["name"], node_object.attrib["uri"])

    return elements

  def update_eta_object(self, element: Variable | VariableList):
    if isinstance(element, Variable):
      logger.debug("Update value of %s (%s)", element.name, element.uri)
      xml = self.__get_variable_xml(element)[0]

      element.adv_text_offset = int(xml.attrib["advTextOffset"])
      element.unit = xml.attrib["unit"]
      element.str_value = xml.attrib["strValue"]
      element.scale_factor = int(xml.attrib["scaleFactor"])
      element.dec_places = int(xml.attrib["decPlaces"])
      element.value = int(float(xml.text))

      if element.adv_text_offset > 0 and len(element.unit) == 0:
        element.variable_type = VariableType.TEXT
      elif re.search(TIMESLOT_REGEX_PATTERN, element.str_value) is not None:
        element.variable_type = VariableType.TIMESLOT
      else:
        element.variable_type = VariableType.DEFAULT

      element.last_updated = datetime.datetime.now()

    elif isinstance(element, VariableList):
      for variable in element.elements.values():
        self.update_eta_object(variable)

  def __get_version_xml(self) -> Element:
    response = get(self.url + API_VERSION_PATH)
    if not response.ok:
      logger.error("Error on communication. (%s, %s) %s", response.status_code, response.url, response.text)
      exit(2)

    return XML(response.text)

  def __get_menu_xml(self) -> Element:
    response = get(self.url + MENU_PATH)
    if not response.ok:
      logger.error("Error on communication. (%s, %s) %s", response.status_code, response.url, response.text)
      exit(2)

    return XML(response.text)

  def __get_variable_xml(self, variable: Variable) -> Element:
    response = get(self.url + VARIABLE_PATH + variable.uri)
    if not response.ok:
      logger.error("Error on communication. (%s, %s) %s", response.status_code, response.url, response.text)
      exit(2)

    return XML(response.text)
