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
from unittest import TestCase

import tests
import tests.tst_helpers
from lor.util import reflection
from tests import fake_pkg
from tests.fake_pkg import mod_with_class
from tests.fake_pkg.mod_with_class import SomeClass
from tests.fake_pkg.nestedexample.another_mod_with_class import SomeOtherClass
from tests.fake_pkg.nestedexample.dir2.mod_with_subclass import SomeSubclass


class TestReflection(TestCase):

    def test_classes_in_pkg_returns_expected_entries(self):
        # Converted into a string because reflection is dynamically loading the class whereas the expected classes are
        # loaded here: the loader is assigning them as "different"

        ret = set(map(str, reflection.classes_in_pkg(fake_pkg)))
        expected_classes = {
            str(SomeClass),
            str(SomeOtherClass),
            str(SomeSubclass),
        }

        self.assertEqual(expected_classes, ret)

    def ignore_subclasses_in_pkg_returns_expected_entries(self):
        # TODO: impl
        ret = set(map(str, reflection.subclasses_in_pkg(fake_pkg, SomeClass)))
        expected_classes = {
            str(SomeSubclass),
        }

        self.assertEqual(expected_classes, ret)

    def test_classes_in_module_returns_expected_entries(self):
        ret = set(map(str, reflection.classes_in_module(mod_with_class)))
        expected_classes = {
            str(SomeClass),
        }

        self.assertEqual(expected_classes, ret)

    def test_load_class_by_name_works(self):
        fully_qualified_name = \
            mod_with_class.SomeClass.__module__ + "." + mod_with_class.SomeClass.__name__

        ret = reflection.load_class_by_name(fully_qualified_name)

        self.assertEqual(str(SomeClass), str(ret))

    def test_filter_subclasses_returns_expected_result(self):
        source_iter = [
            SomeClass,
            SomeClass,
            SomeOtherClass,
            SomeSubclass,
            SomeClass,
            SomeSubclass,
            SomeSubclass,
        ]

        ret = list(reflection.filter_subclasses(SomeClass, source_iter))
        expected_ret = [
            SomeClass,
            SomeClass,
            SomeSubclass,
            SomeClass,
            SomeSubclass,
            SomeSubclass,
        ]

        self.assertEqual(ret, expected_ret)

    def test_is_pkg_returns_True_for_pkg(self):
        self.assertTrue(reflection.is_pkg(tests))

    def test_is_pkg_returns_False_for_module(self):
        self.assertFalse(reflection.is_pkg(tests.tst_helpers))
