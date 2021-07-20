import os
import json

class Generic:
    def __init__(self, config_json: dict):
        for key in config_json:
            self._set_val(self, key, config_json[key])

    
    def _set_val(self, parent, name, value):
        """Very simple loading"""
        usable_parent = self
        if parent:
            usable_parent = parent
        
        if not isinstance(value, dict):
            setattr(usable_parent, name, value)
        else:
            setattr(usable_parent, name, Generic(value))

class Configuration:
    """Uses the settings.json file to load up data. In an actual
    function you'll store these in app settings."""
    @staticmethod
    def load_configuration(config_file:str) -> Generic:
        if not os.path.exists(config_file):
            raise Exception("Config file does not exist")
        
        return_object = None
        with open(config_file, "r") as configuration:
            return_object = configuration.readlines()
            return_object = "\n".join(return_object)
            return_object = json.loads(return_object)
            return_object = Generic(return_object)
        return return_object