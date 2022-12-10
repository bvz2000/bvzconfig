
import configparser
import os

from bvzconfigerror import ConfigError


# ======================================================================================================================
class Config(object):
    """
    Class to manage configurations.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 config_p):
        """
        Setup this wrapper of the default python config parser.

        :param config_p:
                The path to the config file.

        :return:
                Nothing.
        """

        assert type(config_p) is str

        self.config_p = config_p

        if not os.path.exists(config_p):
            msg = "Cannot locate config file: " + os.path.abspath(config_p)
            code = 2
            raise ConfigError(msg, code)

        self.delimited_config_obj = self._read_config_with_delimiters(config_p)
        self.undelimited_config_obj = self._read_config_without_delimiters(config_p)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def config_path(self):
        return self.config_p

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _read_config_with_delimiters(config_p):
        """
        Opens a config file (given by config_p).

        :param config_p:
                The full path to the config file.

        :return:
                A configParser object.
        """

        assert type(config_p) is str

        config_obj = configparser.ConfigParser(allow_no_value=True,
                                               delimiters="=",
                                               empty_lines_in_values=True)

        # Force configparser to maintain capitalization of keys
        config_obj.optionxform = str

        # Read the config.
        config_obj.read(config_p)

        return config_obj

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _read_config_without_delimiters(config_p):
        """
        Opens a config file (given by config_p). This disables the delimiter so that items read are read exactly as
        entered (instead of trying to process key/value pairs).

        :param config_p:
                The full path to the config file.

        :return:
                A configParser object.
        """

        assert type(config_p) is str

        config_obj = configparser.ConfigParser(allow_no_value=True,
                                               delimiters="\n",
                                               empty_lines_in_values=True)

        # Force configparser to maintain capitalization of keys
        config_obj.optionxform = str

        # Read the config
        config_obj.read(config_p)

        return config_obj

    # ------------------------------------------------------------------------------------------------------------------
    def validate(self,
                 sections):
        """
        Makes sure the config file contains the required sections and values. Returns None if all validation checks
        pass.

        :param sections:
                A dictionary where the key is the name of the section that must exist, and the value is a list of tuples
                (item name, item type as a string) that must exist within that section. If only the section must exist,
                but there is no hard and fast rule about the entries, just set this list of items for this section to
                be = None.

                For example: {"section_name": [("count", "int"), ("do_something", "bool")]}
                             {"possibly_empty_section": None}

        :return:
                If the validation fails, returns a three item tuple where the first item is section that failed. The
                second item will either be None (if it is the entire section that is missing) or it will be the item
                that was missing from that section (if the section exists, but the item is missing). The third item will
                either be None if it is one of the previous two types of failures, or a string indicating what the data
                type should have been, but isn't. If the validation succeeds, returns None.
        """

        assert type(sections) is dict
        for section in sections:
            assert type(sections[section]) is list or sections[section] is None

        # Check sections (Only checks the delimited version since it is identical to the undelimited version)
        for section in sections:
            if not self.delimited_config_obj.has_section(section):
                return section, None, None

            if sections[section] is not None:
                for setting, setting_type in sections[section]:
                    if setting:
                        if not self.delimited_config_obj.has_option(section, setting):
                            return section, setting, None
                        if setting_type == "bool":
                            if not self.delimited_config_obj.get(section, setting).upper() in ["TRUE", "FALSE"]:
                                return section, setting, "boolean"
                        if setting_type == "int":
                            try:
                                int(self.delimited_config_obj.get(section, setting))
                            except ValueError:
                                return section, setting, "integer"

        # All good
        return None

    # ------------------------------------------------------------------------------------------------------------------
    def get_list(self,
                 section) -> list:
        """
        Given a section, returns all of the items in that section as a list of strings.

        :param section:
                The name of the section to return.

        :return:
                A list containing all of the items in this section. One line = 1 item in the list.
        """

        assert type(section) is str

        items = [value[0] for value in self.undelimited_config_obj.items(section)]

        return items

    # ------------------------------------------------------------------------------------------------------------------
    def _get_item(self,
                  section,
                  item) -> str:
        """
        Given a section and an item in that section, returns the value of this item.

        :param section:
                The name of the section that contains the item.
        :param item:
                The name of the item to return

        :return:
                The value of the item for this section.
        """

        assert type(section) is str
        assert type(item) is str

        value = self.delimited_config_obj.get(section, item)

        return value

    # ------------------------------------------------------------------------------------------------------------------
    def has_option(self,
                   section,
                   item):
        """
        Returns True if the section and item exists. Essentially a wrapper for the configparser has_option function.

        :param section:
                The section.
        :param item:
                The item.

        :return:
                True if the section and item exist. False otherwise.
        """

        assert type(section) is str
        assert type(item) is str

        return self.delimited_config_obj.has_option(section, item)

    # ------------------------------------------------------------------------------------------------------------------
    def options(self,
                section):
        """
        Just a wrapper for the config parser options function.

        :param section:
                The section we want the options from.

        :return:
                A list of options.
        """

        assert type(section) is str

        return self.delimited_config_obj.options(section)

    # ------------------------------------------------------------------------------------------------------------------
    def get_string(self,
                   section,
                   item) -> str:
        """
        Just a re-branding of _get_item for consistency with the other get functions.


        :param section:
                The name of the section that contains the item.
        :param item:
                The name of the item to return

        :return:
                The value of the item for this section.
        """

        assert type(section) is str
        assert type(item) is str

        result = self._get_item(section, item)
        if result is None:
            result = ""
        return result

    # ------------------------------------------------------------------------------------------------------------------
    def get_integer(self,
                    section,
                    item) -> int:
        """
        Converts the item retrieved to be an integer.


        :param section:
                The name of the section that contains the item.
        :param item:
                The name of the item to return

        :return:
                The value of the item for this section as an integer. If the item cannot be converted to an integer, a
                ValueError is raised.
        """

        assert type(section) is str
        assert type(item) is str

        return int(self._get_item(section, item))

    # ------------------------------------------------------------------------------------------------------------------
    def get_boolean(self,
                    section,
                    item) -> bool:
        """
        Converts the item retrieved to be a boolean.


        :param section:
                The name of the section that contains the item.
        :param item:
                The name of the item to return

        :return:
                The value of the item for this section as a boolean. Accepts True, False (and any case variant of that),
                Yes, No (and their case variants), 0 and 1. Any other values will trigger a ValueError.
        """

        assert type(section) is str
        assert type(item) is str

        value = self._get_item(section, item)
        if value.upper() in ["TRUE", "T", "YES", "Y", "ON", "1"]:
            return True
        if value.upper() in ["FALSE", "F", "NO", "N", "OFF", "0"]:
            return False
        raise ValueError()

    # ------------------------------------------------------------------------------------------------------------------
    def replace_section(self,
                        section,
                        items):
        """
        Given a dictionary of items, replaces all of the existing section (or creates a new section) with the items from
        the dictionary.

        :param section:
                The name of the section to replace (or create if it does not exist).

        :param items:
                A dictionary of items where the key is the option name and the value is the value.

        :return:
                Nothing.
        """

        assert type(section) is str
        assert type(items) is dict

        self.delimited_config_obj.remove_section(section)
        self.undelimited_config_obj.remove_section(section)

        self.delimited_config_obj.add_section(section)
        self.undelimited_config_obj.add_section(section)

        self.merge_section(section, items)

    # ------------------------------------------------------------------------------------------------------------------
    def merge_section(self,
                      section,
                      items):
        """
        Given a dictionary of items, merges the items with the items in already existing in the section. If the section
        does not exist, creates a new one. If an item already exists in the section but is not in the dictionary passed,
        then the item is left alone in that section. If the item exists in both the section and the dictionary, then the
        item will take on the value from the dictionary. If the item is new in the dictionary, it will be added to the
        section.

        :param section:
                The name of the section to merge (or create if it does not exist).

        :param items:
                A dictionary of items where the key is the option name and the value is the value.

        :return:
                Nothing.
        """

        assert type(section) is str
        assert type(items) is dict

        for key, value in items.items():
            self.delimited_config_obj.set(section, key, str(value))
            self.undelimited_config_obj.set(section, key, str(value))
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def get_config_path(self):
        """
        Returns the path to the config file being used.

        :return:
                The path to the config file being used.
        """

        return self.config_p

    # ------------------------------------------------------------------------------------------------------------------
    def save(self):
        """
        Saves the existing configparser back to disk.

        :return:
                Nothing.
        """

        with open(self.config_p, "w") as f:
            self.delimited_config_obj.write(f)
