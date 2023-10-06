# pyETA

I wanted to automate measure some sensor values of my ETA heating system.
So this python package for communicating over the network was born.

## Preconditions on your heating system to use the ETA api

In order to use the ETA REST api you need to ensure the following preconditions (In this order):

1. You must have installed system software version 1.20.0 or higher on your ETAtouch device.
2. You must have registered your ETAtouch device at http://www.meineta.at
3. You must have applied for LAN access at http://www.meineta.at for your ETA-touch device.
4. You must have activated LAN access on your ETAtouch device in the system settings.

## Usage of the package in your code

Basically you need to create a connection to your ETAtouch via an `Eta` object.
From that object the available variables can be read with the `get_nodes()` method.
It will give you a big dictionary with structural information about your system, but no data.

To retrieve the data a `Variable` or `VariableList` object needs to be updated via the `update_eta_object` method.
This will update the given parameter with the retrieved data of you system.

A simple example can be found in the `example_use.py` file at project root.

### Additional flags on the `Eta` class

* `hide_io_variables`: Hides the Input and Output variables. (Default: true)

## More

* [ETAtouch RESTful Webservices Dockumentation V1.2](https://www.meineta.at/javax.faces.resource/downloads/ETA-RESTful-v1.2.pdf.xhtml?ln=default&v=0)
