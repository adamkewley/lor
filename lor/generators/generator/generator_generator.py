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
import os
from argparse import ArgumentParser

from lor import workspace, util
from lor.generator import Generator


class GeneratorGenerator(Generator):

    def description(self):
        return "Generate a code generator"

    def run(self, argv):
        parser = ArgumentParser(description=self.description())
        parser.add_argument("generator_name")

        generator_name = parser.parse_args(argv).generator_name

        ws_path = workspace.get_path()
        if ws_path is None:
            parser.error("Not currently in a workspace")

        ws_package = workspace.get_package_name(ws_path)
        generator_dir = os.path.join(ws_package, "generators", generator_name)

        self.mkdir(generator_dir)
        self.create_file("", os.path.join(generator_dir, "__init__.py"))
        self.mkdir(os.path.join(generator_dir, "templates"))
        generator_modname = generator_name + "_generator.py"
        generator_classname = util.to_camel_case(generator_name)
        self.render_template(
            "generator.py.jinja2",
            os.path.join(generator_dir, generator_modname),
            {
                "generator_classname": generator_classname
            })
