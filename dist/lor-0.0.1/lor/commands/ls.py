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
import importlib

import os

import sys
from luigi import Task

from lor.util import reflection
from lor.util.cli import CliCommand


class LsCommand(CliCommand):

    def name(self):
        return "ls"

    def description(self):
        return "list Luigi `Tasks` in a python module or package"

    def run(self, argv):
        parser = argparse.ArgumentParser(description=self.description())
        parser.add_argument(
            "module_or_package",
            type=str,
            nargs="+",
            help="Name of the module(s). Example: 'lor.tasks.tar'")
        parsed_args = parser.parse_args(argv)

        sys.path.insert(0, os.getcwd())

        for mod_or_pkg_name in parsed_args.module_or_package:
            self.__print_tasks_in_mod_or_pkg(mod_or_pkg_name)

    def __print_tasks_in_mod_or_pkg(self, module_name):
        mod_or_pkg = importlib.import_module(module_name)
        if reflection.is_pkg(mod_or_pkg):
            all_classes = reflection.classes_in_pkg(mod_or_pkg)
        else:
            all_classes = reflection.classes_in_module(mod_or_pkg)

        task_classes = reflection.filter_subclasses(Task, all_classes)

        for task_class in task_classes:
            self.__print_task(task_class)

    def __print_task(self, task_class):
        print(task_class.__module__ + "." + task_class.__name__)
