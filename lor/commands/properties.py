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
"""Module for a command that lists runtime property keys + values.
"""
import argparse

import lor._internal
from lor import props
from lor.util import cli
from lor.util.cli import CliCommand


class PropertiesCommand(CliCommand):

    def name(self):
        return "properties"

    def description(self):
        return "list all properties, as used by LoR at runtime"

    def run(self, argv):
        parser = argparse.ArgumentParser(description=self.description())
        cli.add_properties_override_arg(parser)
        lor_args, ignored_args = parser.parse_known_args(argv)

        property_overrides = cli.extract_property_overrides(lor_args)
        lor._internal.bootstrap_globals(property_overrides)

        for k, v in props.get_all().items():
            print("{k}={v}".format(k=k, v=v))
