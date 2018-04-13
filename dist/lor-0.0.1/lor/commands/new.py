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

from lor import workspace
from lor.util.cli import CliCommand


class NewCommand(CliCommand):

    def name(self):
        return "new"

    def description(self):
        return "create a new LoR workspace"

    def run(self, argv):
        parser = argparse.ArgumentParser(description=self.description())
        parser.add_argument(
            "workspace_path",
            type=str,
            help="Path to newly-created workspace")

        parsed_args = parser.parse_args(argv)

        workspace.create(parsed_args.workspace_path)
        workspace.run_install_script(parsed_args.workspace_path)
