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
from luigi.cmdline_parser import CmdlineParser

from lor.util import cli
from lor.util.cli import CliCommand


class ExplainCommand(CliCommand):

    def name(self):
        return "explain"

    def description(self):
        return "explain a task"

    def run(self, argv):
        parser = argparse.ArgumentParser(description=self.description())

        cli.add_properties_override_arg(parser)
        lor_args, luigi_args = parser.parse_known_args(argv)

        property_overrides = cli.extract_property_overrides(lor_args)
        lor._internal.bootstrap_globals(property_overrides)

        with CmdlineParser.global_instance(luigi_args) as cp:
            task_obj = cp.get_task_obj()
            explain(task_obj)


def explain(task_obj):
    explanation = generate_task_explanation(task_obj)
    print(explanation)


def generate_task_explanation(task_obj):
    return "\n".join([
        generate_header(task_obj),
        generate_inputs(task_obj),
        generate_outputs(task_obj),
        generate_depends(task_obj),
    ])


def generate_header(task_obj):
    if hasattr(task_obj, "description"):
        return task_obj.__class__.__name__ + ": " + getattr(task_obj, "description")
    else:
        return task_obj.__name__


def generate_inputs(task_obj):
    ret = "Inputs:\n"
    for name in vars(task_obj):
        prop = getattr(task_obj, name)
        if isinstance(prop, luigi.Parameter):
            ret += "  {name}: {prop}\n".format(name=name, prop=prop)

    return ret


def generate_outputs(task_obj):
    ret = "Outputs:\n"

    task_outputs = task_obj.output()
    try:
        for task_output in task_outputs:
            ret += task_output.path + "\n"
    except TypeError:
        ret += task_outputs.path

    return ret


def generate_depends(task_obj):
    return "Depends On:\n  {reqs}".format(reqs=task_obj.requires())
