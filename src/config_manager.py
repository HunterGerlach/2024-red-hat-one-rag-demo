import yaml
import os
import streamlit as st

class ConfigManager:
    """ Manages application configuration. """
    
    @staticmethod
    def load_config_details():
        """ Load configuration details from a YAML file. """
        config_path = os.getenv('CONFIG_PATH', 'config.yaml')
        try:
            with open(config_path, 'r') as config_file:
                configurations = yaml.safe_load(config_file)
            return configurations
        except FileNotFoundError:
            st.error("Configuration file not found.")
            return None
        except yaml.YAMLError as exc:
            st.error(f"Error parsing configuration file: {exc}")
            return None

    @staticmethod
    def validate_configurations(configurations):
        """ Validate that the configuration is not empty and return a boolean. """
        is_valid = bool(configurations) and all(key in configurations for key in ["redis", "inference_server"])
        if not is_valid:
            st.error("Configuration details are missing or incomplete.")
        return is_valid
