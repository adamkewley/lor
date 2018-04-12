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
"""Module for visualizing Luigi task graphs
"""
import argparse
import types

import luigi
import networkx
from luigi.cmdline_parser import CmdlineParser
from networkx.drawing.nx_pydot import to_pydot

import lor._internal
from lor import util
from lor.util import cli
from lor.util.cli import CliCommand


class DotCommand(CliCommand):

    def name(self):
        return "dot"

    def description(self):
        return "Convert a task into DOT graph format. DOT files can be visualized with external tools such as graphviz"

    def run(self, argv):
        parser = argparse.ArgumentParser(description=self.description())

        # TODO: Replace the workspace CLI bootstrapping a func
        cli.add_properties_override_arg(parser)
        lor_args, luigi_args = parser.parse_known_args(argv)

        property_overrides = cli.extract_property_overrides(lor_args)
        lor._internal.bootstrap_globals(property_overrides)

        with CmdlineParser.global_instance(luigi_args) as cp:
            task_obj = cp.get_task_obj()
            print_as_dot(task_obj)


def print_as_dot(task):
    g = networkx.DiGraph()
    recursively_traverse_task(g, task)
    print(to_pydot(g))


def recursively_traverse_task(graph, task, parent_task_name=None, previously_traversed_task_names=None):
    if previously_traversed_task_names is None:
        previously_traversed_task_names = {}

    if task in previously_traversed_task_names:
        name = previously_traversed_task_names[task]
    else:
        name = type(task).__name__ + "_" + util.base36_str(3)
        previously_traversed_task_names[task] = name

    if parent_task_name is not None:
        graph.add_edge(parent_task_name, name)
    else:
        graph.add_node(name)

    top_lvl_labels = {name: name}

    requirements = task.requires()
    if isinstance(requirements, luigi.Task):
        labels = recursively_traverse_task(graph, requirements, name, previously_traversed_task_names)
        return util.merge(top_lvl_labels, labels)
    elif isinstance(requirements, dict):
        labels = top_lvl_labels
        for k, v in requirements.items():
            sub_labels = recursively_traverse_task(graph, v, name, previously_traversed_task_names)
            labels = util.merge(labels, sub_labels)
        return labels
    elif isinstance(requirements, types.GeneratorType):
        labels = top_lvl_labels
        for task in requirements:
            sub_labels = recursively_traverse_task(graph, task, name, previously_traversed_task_names)
            labels = util.merge(labels, sub_labels)
    else:
        return top_lvl_labels
