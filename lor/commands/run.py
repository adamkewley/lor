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
import argparse

import luigi
import lor._internal

from lor.util import cli
from lor.util.cli import CliCommand


class RunCommand(CliCommand):

    epilog = """
    This command is effectively an alias for the base `luigi` command. The only addition is that this command *also* 
    allows overrides that are specific to LoR (e.g. overriding a property value).
    """

    def name(self):
        return "run"

    def description(self):
        return "Run a task"

    def run(self, argv):
        parser = argparse.ArgumentParser(description=self.description())
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.epilog = self.epilog

        cli.add_properties_override_arg(parser)
        lor_args, luigi_args = parser.parse_known_args(argv)

        property_overrides = cli.extract_property_overrides(lor_args)
        lor._internal.bootstrap_globals(property_overrides)

        luigi.run(luigi_args)
