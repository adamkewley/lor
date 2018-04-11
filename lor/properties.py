# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Property loading support

Luigi projects typically require loading configuration properties at runtime. *Where* those properties should be loaded
from depends on the situation. For example, domain specific knowledge might be put into the project itself
(e.g. etc/properties.yml) whereas user logins might be placed in the user's home folder.

This module contains basic abstractions for loading properties from various sources transparently. This allows LoR
workspace tasks to just "get" a property without having to worry about *where* it came from. How the various property
sources are prioritized is dictated by the workspace implementation.
"""
import os

from lor import util


class PropertyLoader:
    """Abstract class for loading properties.

    `PropertyLoader`s allow runtime associative lookup of a property's value. This abstraction is similar to a standard
     python dict but `PropertyLoaders`s are read-only once initialized and have human-readable names. Names make
     debugging easier: instead of a vague "KeyError", more descriptive errors are possible.
    """

    def get_name(self):
        """Returns a human-readable name for the `PropertyLoader`.

        :return: A human-readable name for the `PropertyLoader` instance.
        """
        raise NotImplementedError()

    def try_get(self, prop_name):
        """Returns the value of a property identified by `prop_name` if a value can be found. Otherwise, returns None.

        If there was an issue loading the property (e.g. because they are loaded from a disk) a RuntimeError is raised.

        :param prop_name: Identifier of the property to get
        :return: The value of the property if it was found; otherwise, none.
        """
        raise NotImplementedError()

    def get(self, prop_name):
        """Returns the value of a property identified by `prop_name`.

        Attempts to get a property by its identifier. If a value cannot be found, a KeyError is raised. If there was an
        issue loading the property (e.g. because they are loaded from a disk) a RuntimeError is raised.

        :param prop_name: Identifier of the property to get
        :return: The value of the property
        """
        raise NotImplementedError()

    def get_all(self):
        """Returns all properties the loader can load as a dict of key-value pairs.

        :return: A dict (string, string) containing all properties
        """
        raise NotImplementedError()


class DictPropertyLoader(PropertyLoader):
    """A `PropertyLoader` loader that is backed by an in-memory python dict.
    """

    def __init__(self, name, property_dict):
        self.name = name
        self.property_dict = property_dict

    def get_name(self):
        return self.name

    def try_get(self, prop_name):
        return self.property_dict.get(prop_name)

    def get(self, prop_name):
        return util.try_get_val_or_key_error(self.property_dict, prop_name)

    def get_all(self):
        return self.property_dict.copy()


class YAMLFilePropertyLoader(PropertyLoader):
    """A `PropertyLoader` that loads property values from a YAML file.

    Eagerly loads the provided YAML file in order to "fail fast". Does not attempt to reload the source file at runtime.
    """

    def __init__(self, path_to_yaml_file):
        if not os.path.exists(path_to_yaml_file):
            raise FileNotFoundError("{path_to_yaml_file}: No such file: required as a YAML file containing properties".format(path_to_yaml_file=path_to_yaml_file))

        self.path_to_yaml_file = path_to_yaml_file

        try:
            self.property_dict = util.read_yaml(path_to_yaml_file)
        except Exception as ex:
            raise RuntimeError("{path_to_yaml_file}: Error loading as a standard YAML file: required as a properties file".format(path_to_yaml_file=path_to_yaml_file)) from ex

    def get_name(self):
        return self.path_to_yaml_file

    def try_get(self, prop_name):
        return self.property_dict.get(prop_name)

    def get(self, prop_name):
        return util.try_get_val_or_key_error(self.property_dict, prop_name)

    def get_all(self):
        return self.property_dict


def get_property_from_list_of_loaders(property_loaders, prop_name):
    """Returns a property's value, if a value could be loaded from a list of PropertyLoaders.

    Goes through each `PropertyLoader` in `property_loaders` in order, attempting to get the property from that loader.
    Once a value for the property is found, returns that value. If the property cannot be found in all property loaders,
    raises a KeyError.

    :return The property's value
    """
    for property_loader in property_loaders:
        maybe_ret = property_loader.try_get(prop_name)
        if maybe_ret is not None:
            return maybe_ret

    prop_loader_names = util.or_join(list(map(lambda loader: loader.get_name(), property_loaders)))
    err_msg = "{prop_name}: No such property found in {loaders}".format(prop_name=prop_name, loaders=prop_loader_names)

    raise KeyError(err_msg)


def merge_list_of_property_loaders(property_loaders):
    """Returns a dict containing the merge product of all property loaders.

    Earlier elements in `property_loaders` take higher priority over lower elements
    """

    ret = {}

    for property_loader in reversed(property_loaders):
        loader_props = property_loader.get_all()
        ret = util.merge(ret, loader_props)

    return ret
