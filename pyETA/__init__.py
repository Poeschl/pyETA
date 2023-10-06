import logging
import re
from xml.etree.ElementTree import XML, Element

from requests import get

from models import Node, VariableList, Variable, EtaObject

SUPPORTED_API_VERSIONS = ["1.2", "1.1", "1.0"]
API_VERSION_PATH = "/user/api"
MENU_PATH = "/user/menu"
VARIABLE_PATH = "/user/var"

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
    logger.info("Initialized ETA connection to %s", host)

  def __check_compatibility(self):
    xml = self.__get_version_xml()

    api_element = xml[0]
    if not (api_element.tag.endswith("api") and api_element.attrib["version"] in SUPPORTED_API_VERSIONS):
      logger.error("Error: Not supported API version. Your ETA Rest Version is not supported by this library.")
      logger.error("Detected API version: '%s' Supported versions: %s", api_element.attrib["version"], SUPPORTED_API_VERSIONS)
      exit(1)

  def get_nodes(self) -> dict[str, Node]:
    """
    Retrieves all available device node of you ETA heating system.
    The nodes are not filled with data but represent the structure of the available variables.
    :return: A dict with names of the nodes and a node object with nested variables.
    """
    xml = self.__get_menu_xml()
    nodes: dict[str, Node] = {}

    node: Element
    for node in xml[0]:
      node_elements = self.__parse_object_list(node)

      nodes[node.attrib["name"]] = Node(node.attrib["name"], node.attrib["uri"], node_elements)

    return nodes

  def __parse_object_list(self, root: Element) -> dict[str, EtaObject]:
    elements: dict[str, EtaObject] = {}
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
        elements[node_object.attrib["name"]] = (Variable(node_object.attrib["name"], node_object.attrib["uri"]))

    return elements

  def __get_version_xml(self) -> XML:
    response = get(self.url + API_VERSION_PATH)
    if not response.ok:
      logger.error("Error on communication. (%s, %s) %s", response.status_code, response.url, response.text)
      exit(2)

    return XML(response.text)

  def __get_menu_xml(self) -> XML:
    response = get(self.url + MENU_PATH)
    if not response.ok:
      logger.error("Error on communication. (%s, %s) %s", response.status_code, response.url, response.text)
      exit(2)

    return XML(response.text)
