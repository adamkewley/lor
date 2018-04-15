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
import inspect
import os
import tempfile
from unittest import TestCase

import tests.fixture_pkg.generators.with_templates.with_templates_generator
from lor import workspace, util
from lor.generator import Generator
from lor.test import TemporaryWorkspace, TemporaryEnv
from tests import tst_helpers
from tests.fixture_pkg.generators.with_templates.with_templates_generator import WithTemplatesGenerator
from tests.fixture_pkg.generators.without_templates.without_templates_generator import WithoutTemplatesGenerator


class MinimalGeneratorImpl(Generator):

    def run(self, argv):
        pass


class GeneratorWithOverridableSourceAndDest(Generator):

    def __init__(self, source_roots_val, destination_root_val):
        self.source_roots_val = source_roots_val
        self.destination_root_val = destination_root_val

    def run(self, argv):
        pass

    def source_roots(self):
        return self.source_roots_val

    def destination_root(self):
        return self.destination_root_val


class TestGenerator(TestCase):

    def test_run_raises_NotImplementedError_on_base_class(self):
        generator = Generator()
        with self.assertRaises(NotImplementedError):
            generator.run([])

    def test_description_returns_objects_name_if_not_overridden(self):
        generator = Generator()
        with self.assertRaises(NotImplementedError):
            generator.description()

    def test_source_roots_defaults_to_implementation_templates_dir_if_exists(self):
        fixture_generator_with_templates_dir = WithTemplatesGenerator()
        returned_source_roots = fixture_generator_with_templates_dir.source_roots()

        fixture_path = tests.fixture_pkg.generators.with_templates.with_templates_generator.__path__

        expected_source_roots = [
            os.path.join(fixture_path, "templates")
        ]

        self.assertEqual(expected_source_roots, returned_source_roots)

    def test_source_roots_detauls_to_implementation_package_path_if_templates_doesnt_exist(self):
        fixture_generator_without_templates_dir = WithoutTemplatesGenerator()
        returned_source_roots = fixture_generator_without_templates_dir.source_roots()

        package_path = os.path.dirname(inspect.getsourcefile(inspect.getmodule(fixture_generator_without_templates_dir)))

        self.assertEqual(package_path, returned_source_roots)

    def test_destination_root_returns_workspace_on_base_class(self):
        with TemporaryWorkspace() as ws:
            generator = Generator()
            self.assertEqual(ws.get_path(), generator.destination_root())

    def test_destination_root_raises_AssertionError_if_not_in_a_workspace(self):
        generator = Generator()
        tmp_dir = tempfile.mkdtemp()

        with TemporaryEnv():
            workspace._set_path(None)
            os.chdir(tmp_dir)

            with self.assertRaises(AssertionError):
                generator.destination_root()

    def test_render_template_renders_template_into_destination_root(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()
        generator = GeneratorWithOverridableSourceAndDest(source_roots, destination_root)
        output_filename = util.base36_str()
        foo_val = util.base36_str()

        generator.render_template("example.txt.jinja2", output_filename, {"foo": foo_val})

        expected_output_path = os.path.join(destination_root, output_filename)

        self.assertTrue(os.path.exists(expected_output_path))

        file_content = util.read_file_to_string(expected_output_path)

        self.assertTrue("foo\n", file_content)

    def test_render_template_creates_non_existent_subdirs(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()
        generator = GeneratorWithOverridableSourceAndDest(source_roots, destination_root)
        foo_val = util.base36_str()

        output_relpath = os.path.join(util.base36_str(), util.base36_str())

        generator.render_template("example.txt.jinja2", output_relpath, {"foo": foo_val})

        expected_output_path = os.path.join(destination_root, output_relpath)

        self.assertTrue(os.path.exists(expected_output_path))

        file_content = util.read_file_to_string(expected_output_path)

        self.assertTrue(foo_val + "\n", file_content)

    def test_render_template_raises_FileNotFound_if_template_does_not_exist(self):
        source_roots = [tempfile.mkdtemp()]
        destination_root = tempfile.mkdtemp()
        generator = GeneratorWithOverridableSourceAndDest(source_roots, destination_root)

        with self.assertRaises(FileNotFoundError):
            generator.render_template("doesnt-exist", os.path.join(destination_root, util.base36_str()), {})

    def test_render_template_raises_FileExistsError_if_file_already_exists_in_destination(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()

        file_already_in_dest = util.base36_str()
        open(os.path.join(destination_root, file_already_in_dest), "a").close()

        generator = GeneratorWithOverridableSourceAndDest(source_roots, destination_root)

        with self.assertRaises(FileExistsError):
            generator.render_template("example.txt.jinja2", file_already_in_dest, {})

    def test_create_file_creates_file_with_content(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()
        generator = GeneratorWithOverridableSourceAndDest(source_roots, destination_root)

        content = util.base36_str()
        filename = util.base36_str()

        generator.create_file(content, filename)

        output_path = os.path.join(destination_root, filename)
        self.assertTrue(os.path.exists(output_path))

        written_content = util.read_file_to_string(output_path)

        self.assertEqual(content, written_content)

    def test_create_file_creates_non_existent_subdirs(self):
        self.assertTrue(False)

    def test_create_file_raises_FileExistsError_if_file_already_exists(self):
        self.assertTrue(False)

    def test_copy_file_copies_file_to_destination(self):
        self.assertTrue(False)

    def test_copy_file_raises_FileNotFoundError_if_source_does_not_exist(self):
        self.assertTrue(False)

    def test_copy_file_raises_FileExistsError_if_destination_already_exists(self):
        self.assertTrue(False)

    def test_mkdir_makes_empty_dir(self):
        self.assertTrue(False)

    def test_mkdir_raises_FileExistsError_if_dir_already_exists(self):
        self.assertTrue(False)
