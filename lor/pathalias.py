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
"""Path aliasing support

Luigi projects typically involve working with resources addressed via paths/URIs. Writing the code necessary to build
those paths is error-prone and usually involves writing a bunch of `join` functions in the Luigi task. That code then
needs to be edited whenever paths change.

This module implements LoR support for `pathaliases` - a tiny python library for pathalias YAML files. The files contain
hierarchies of paths. For example:

dir1/:
  subdir/:
    ${var}/:
      alias: FOO


With that file in place, downstream clients can then just write `resolve("FOO", {"var": "bar"})` (or similar) and the
engine builds the actual path at runtime. This enables tasks to focus on using aliases (e.g. `FOO`) rather than
building paths, which makes it easier to change locations later down the line.

The YAML file format was chosen so that a pathaliases parser could be built from scratch in another language trivially.

"""

import os

import pathaliases

from lor import util, properties


def resolve(alias_file_path, alias, property_loaders=None):
    """
    Resolve a path from its alias via a pathaliases YAML file.

    :param alias_file_path: Path to the aliases file
    :param alias: The alias to resolve
    :param property_loaders: A list of PropertyLoaders to resolve the aliases file against
    :return: The resolved path
    """
    if property_loaders is None:
        property_loaders = []

    if not os.path.exists(alias_file_path):
        error_msg = "{alias_file_path}: cannot resolve: no such file (needed to resolve alias '{alias}')".format(alias_file_path=alias_file_path, alias=alias)
        raise FileNotFoundError(error_msg)

    all_aliases = pathaliases.resolve_yaml_to_path_strings(alias_file_path, env=properties.merge_list_of_property_loaders(property_loaders))

    if alias in all_aliases:
        return all_aliases.get(alias)
    else:
        relpath = os.path.relpath(alias_file_path, os.getcwd())
        error_start = "{alias}: not found in {relpath}".format(alias=alias, relpath=relpath)

        maybe_suggestions = util.try_construct_suggestions_msg(all_aliases, alias)
        if maybe_suggestions is not None:
            error_msg = error_start + ": " + maybe_suggestions
        else:
            error_msg = error_start

        raise KeyError(error_msg)
