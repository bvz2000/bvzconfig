
import configparser
import os

from bvzconfigerror import ConfigError


# ======================================================================================================================
class Config(object):
    """
    Class to manage configurations. Subclassed from the default python config parser.
    """

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self,
                 config_p):
        """
        Setup this subclass of the default python config parser.

        :param config_p:
                The path to the config file.

        :return:
                Nothing.
        """

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

                For example: {"section_name": [("count", "int"), ("do_something", "bool")}
                             {"possibly_empty_section": None}

        :return:
                If the validation fails, returns a three item tuple where the first item is section that failed. The
                second item will either be None (if it is the entire section that is missing) or it will be the item
                that was missing from that section (if the section exists, but the item is missing. The third item will
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
    #
    # # ------------------------------------------------------------------------------------------------------------------
    # def save(self):
    #     """
    #     Writes the config parser back out to disk.
    #
    #     :return:
    #             Nothing.
    #     """
    #
    #     try:
    #         with open(self.config_p, "w") as f:
    #             self.write(f)
    #     except IOError as err:
    #         if err.errno == 13:
    #             raise IOError("You do not have write permission for: " + self.config_p)
    #         else:
    #             raise

    # ------------------------------------------------------------------------------------------------------------------
    def get_list(self,
                 section) -> list:
        """
        Given a section, returns all of the items in that section as a list.

        :param section:
                The name of the section to return.

        :return:
                A list containing all of the items in this seciton. One line = 1 item in the list.
        """

        assert type(section) is str

        items = [value[0] for value in self.undelimited_config_obj.items(section)]

        return items

    # ------------------------------------------------------------------------------------------------------------------
    def get_item(self,
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
