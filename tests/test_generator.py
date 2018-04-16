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


class ConfigurableSourceDestGenerator(Generator):

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

    def test_run_default_raises_NotImplementedError(self):
        non_subclassed_generator = Generator()
        with self.assertRaises(NotImplementedError):
            non_subclassed_generator.run([])

    def test_description_default_returns_object_name(self):
        non_subclassed_generator = Generator()
        returned_description = non_subclassed_generator.description()

        self.assertEqual("Generator", returned_description)

    def test_source_roots_default_returns_implementation_templates_dir_if_exists(self):
        fixture_generator_with_templates_dir = WithTemplatesGenerator()
        actual_source_roots = fixture_generator_with_templates_dir.source_roots()

        fixture_path = tests.fixture_pkg.generators.with_templates.__path__[0]

        expected_source_roots = [
            os.path.join(fixture_path, "templates/")
        ]

        self.assertEqual(expected_source_roots, actual_source_roots)

    def test_source_roots_default_returns_implementation_package_path_if_templates_doesnt_exist(self):
        fixture_generator_without_templates_dir = WithoutTemplatesGenerator()
        actual_source_roots = fixture_generator_without_templates_dir.source_roots()

        implementation_module_path = inspect.getsourcefile(inspect.getmodule(fixture_generator_without_templates_dir))
        implementation_package_path = os.path.dirname(implementation_module_path)

        expected_source_roots = [
            implementation_package_path,
        ]

        self.assertEqual(expected_source_roots, actual_source_roots)

    def test_destination_root_default_returns_workspace(self):
        non_subclassed_generator = Generator()

        with TemporaryWorkspace() as workspace_path:
            actual_destination_root = non_subclassed_generator.destination_root()

            self.assertEqual(workspace_path, actual_destination_root)

    def test_destination_root_default_raises_AssertionError_if_not_in_a_workspace(self):
        non_subclassed_generator = Generator()
        empty_dir = tempfile.mkdtemp()

        with TemporaryEnv():
            workspace._set_path(None)
            os.chdir(empty_dir)

            with self.assertRaises(AssertionError):
                non_subclassed_generator.destination_root()

    def test_render_template_writes_rendered_template_to_destination_root(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator(source_roots, destination_root)
        output_filename = util.base36_str()
        foo_val = util.base36_str()

        generator.render_template("example.txt.jinja2", output_filename, {"foo": foo_val})

        expected_output_path = os.path.join(destination_root, output_filename)

        self.assertTrue(os.path.exists(expected_output_path))

        file_content = util.read_file_to_string(expected_output_path)

        self.assertTrue("foo\n", file_content)

    def test_render_template_creates_subdirs_when_required(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator(source_roots, destination_root)
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
        generator = ConfigurableSourceDestGenerator(source_roots, destination_root)

        with self.assertRaises(FileNotFoundError):
            generator.render_template("doesnt-exist", os.path.join(destination_root, util.base36_str()), {})

    def test_render_template_raises_FileExistsError_if_destination_already_exists(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()

        file_already_in_dest = util.base36_str()
        self.__create_empty_file(os.path.join(destination_root, file_already_in_dest))

        generator = ConfigurableSourceDestGenerator(source_roots, destination_root)

        with self.assertRaises(FileExistsError):
            generator.render_template("example.txt.jinja2", file_already_in_dest, {})

    def __create_empty_file(self, path):
        open(path, "a").close()

    def test_create_file_creates_file_with_content(self):
        source_roots = [tst_helpers.fixture("templates/")]
        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator(source_roots, destination_root)

        content = util.base36_str()
        filename = util.base36_str()

        generator.create_file(content, filename)

        output_path = os.path.join(destination_root, filename)
        self.assertTrue(os.path.exists(output_path))

        written_content = util.read_file_to_string(output_path)

        self.assertEqual(content, written_content)

    def test_create_file_creates_subdirs_when_required(self):
        source_roots = [tempfile.mkdtemp()]
        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator(source_roots, destination_root)
        provided_content = util.base36_str()

        output_relpath = os.path.join(util.base36_str(), util.base36_str())

        generator.create_file(provided_content, output_relpath)

        expected_output_path = os.path.join(destination_root, output_relpath)

        self.assertTrue(os.path.exists(expected_output_path))

        written_content = util.read_file_to_string(expected_output_path)

        self.assertTrue(provided_content, written_content)

    def test_create_file_raises_FileExistsError_if_file_already_exists(self):
        source_roots = [tempfile.mkdtemp()]
        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator(source_roots, destination_root)

        path_already_at_dest = util.base36_str()
        self.__create_empty_file(os.path.join(destination_root, path_already_at_dest))

        with self.assertRaises(FileExistsError):
            generator.create_file(util.base36_str(), path_already_at_dest)

    def test_copy_file_copies_file_to_destination(self):
        source_root = tempfile.mkdtemp()
        file_at_source = util.base36_str()
        content_in_source_file = util.base36_str()

        with open(os.path.join(source_root, file_at_source), "w") as f:
            f.write(content_in_source_file)

        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator([source_root], destination_root)
        destination_path = util.base36_str()

        generator.copy_file(file_at_source, destination_path)

        expected_output_file = os.path.join(destination_root, destination_path)

        self.assertTrue(os.path.exists(expected_output_file))

        content_in_destination_file = util.read_file_to_string(expected_output_file)

        self.assertEqual(content_in_source_file, content_in_destination_file)

    def test_copy_file_raises_FileNotFoundError_if_source_does_not_exist(self):
        empty_source_root = tempfile.mkdtemp()
        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator([empty_source_root], destination_root)

        with self.assertRaises(FileNotFoundError):
            generator.copy_file("doesnt-exist", "doesnt-matter")

    def test_copy_file_raises_FileExistsError_if_destination_already_exists(self):
        source_root = tempfile.mkdtemp()
        destination_root = tempfile.mkdtemp()

        source_path = util.base36_str()
        self.__create_empty_file(os.path.join(source_root, source_path))

        destination_path = util.base36_str()
        self.__create_empty_file(os.path.join(destination_root, destination_path))

        generator = ConfigurableSourceDestGenerator([source_root], destination_root)

        with self.assertRaises(FileExistsError):
            generator.copy_file(source_path, destination_path)

    def test_mkdir_makes_empty_dir(self):
        destination_root = tempfile.mkdtemp()
        destination_path = util.base36_str()
        generator = ConfigurableSourceDestGenerator([tempfile.mkdtemp()], destination_root)

        generator.mkdir(destination_path)

        expected_output_path = os.path.join(destination_root, destination_path)

        self.assertTrue(os.path.exists(expected_output_path))
        self.assertTrue(os.path.isdir(expected_output_path))
        self.assertEqual(0, len(os.listdir(expected_output_path)))

    def test_mkdir_raises_FileExistsError_if_dir_already_exists(self):
        destination_root = tempfile.mkdtemp()
        generator = ConfigurableSourceDestGenerator([tempfile.mkdtemp()], destination_root)

        destination_path = util.base36_str()
        self.__create_empty_file(os.path.join(destination_root, destination_path))

        with self.assertRaises(FileExistsError):
            generator.mkdir(destination_path)
