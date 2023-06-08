"""
config.py

Contains the config class.
Contains the config class which is
used to store the configuration data
of the application.
"""

#-------------------------------------------------------------------#

import json
import os
import decimal

from src.server.api_config import APIJsons

#-------------------------------------------------------------------#

class Config:
    """
    Stores the configuration data of the application.
    """
    DEFAULT = "default"
    CUSTOM = "custom"
    def __init__(self, app) -> None:
        """
        Reads the json file (./config.json).
        Shuts down the process if an error occurs.

        The json file is used to configure the images and the shopping menus
        (items, prices, etc.)
        """
        self.loggers = app.loggers
        self.app = app

        self.api_config = APIJsons(self)
        self.name = self.DEFAULT
        self.loaded_config = {}
        self.initial_config = {}
        self.custom_config = {}

        self.setup_custom()
        self.default_config = self.load(self.DEFAULT)

    def generate_json(self, name,  json_retrieved:json, api:bool=0) -> bool:
        """
        Generate a json file corresponding
        to the request response given.
        """
        if api:
            path = "api"
        else:
            path = ""

        with open(os.path.join(os.getcwd(),"data","json", path, f"{name}.json"),
                  'w',
                  encoding="utf-8") as file:
            file.write(json.dumps(json_retrieved, indent=4))

    def setup_custom(self) -> None:
        """
        Setup the custom config.
        """
        if not os.path.exists(os.path.join(os.getcwd(),"data","json", "custom.json")):
            self.generate_json("custom", json.loads("{'custom':{}}"))
        self.custom_config = self.load("custom")
        self.cat_refill(self.custom_config)

    def load(self, file_name:str=None, api:bool=0) -> dict:
        """
        Loads the json file onto loaded_config and copies it to initial_config.
        Returns a dictionary containing the json file data.
        """
        if file_name is None:
            return {}
        dictionary = {}

        if api:
            path = "api"
        else:
            path = ""

        with open(os.path.join(os.getcwd(),"data","json", path, f"{file_name}.json"),
                  'r',
                  encoding="utf-8") as file:
            json_content = file.read()
        try:
            dictionary.update(json.loads(json_content, parse_float=decimal.Decimal))
        except json.JSONDecodeError as decode_err:
            self.loggers.log.warning("Error while parsing the config.json file at line %s",
                                     decode_err.lineno)
            self.app.close()

        self.name = file_name
        self.loaded_config = dictionary["data"].copy()
        self.cat_refill(self.loaded_config)
        self.initial_config = self.loaded_config.copy()
        return dictionary["data"]

    def change_price(self, toggle, item_name, new_price):
        """
        Changes the price of an item.
        """
        items = self.loaded_config["Shopping"][toggle]['items']
        for index, item in enumerate(items):
            if item['name'] == item_name:
                items[index]['price'] = decimal.Decimal(new_price)
                break

    def cat_refill(self, config) -> None:
        """
        Concatenates the refill toggle to the loaded json.
        """
        with open(os.path.join(os.getcwd(),"data","json", "refill.json"),
                  'r',
                  encoding="utf-8") as file:
            refill_content = file.read()

        refill_dict = json.loads(refill_content, parse_float=decimal.Decimal)
        config.append(refill_dict['refill'])

    def get_loaded_categories(self) -> list:
        """
        Returns the categories of the loaded config.
        """
        return [product_type["product_type"] for product_type in self.loaded_config]
