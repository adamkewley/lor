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
"""Utilities for reflecting over python
"""
import importlib
import inspect
import pkgutil
import sys
from inspect import isclass


def subclasses_in_pkg(package, superclass):
    """Returns an iterable of classes in a package which are subclasses of a superclass.

    :param package: The package to search in
    :param superclass: The superclass to filter against
    :return: An iterable of classes in `package` which are subclasses of `superclass`
    """
    return filter_subclasses(superclass, classes_in_pkg(package))


def filter_subclasses(superclass, iter):
    """Returns an iterable of class obects which are subclasses of `superclass` filtered from a source iteration.

    :param superclass: The superclass to filter against
    :return: An iterable of classes which are subclasses of `superclass`
    """
    return filter(lambda klass: issubclass(klass, superclass), iter)


def is_pkg(mod_or_pkg):
    """Returns True if `mod_or_pkg` is a package"""
    return inspect.ismodule(mod_or_pkg) and hasattr(mod_or_pkg, "__path__")


def classes_in_pkg(package):
    """Returns an iterable of python classes found in `package`

    :param package: The package to search in
    :return: An iterable of classes found in `package`
    """
    package_members = pkgutil.walk_packages(package.__path__, prefix=package.__name__ + ".")

    for module_finder, module_name, is_pkg in package_members:
        if not is_pkg:
            try:
                module_loader = module_finder.find_module(module_name)
                module = module_loader.load_module()
                yield from classes_in_module(module)
            except Exception as ex:
                print(module_name + ": cannot reflect: {ex}".format(ex=ex), file=sys.stderr)


def classes_in_module(module):
    """Returns an iterable of python classes found in `module`

    :param module The module to search in
    :return An iterable of classes found in `module`
    """
    for class_name, klass in inspect.getmembers(module):
        if isclass(klass) and klass.__module__ == module.__name__:
            yield klass


def load_class_by_name(full_class_name):
    """Load a class by its fully-qualified name.

    "Fully qualified name" is a LoR-specific. It is PACKAGE.MODULE.CLASS_NAME. Examples:

    - lor.tasks.fs.EnsureExistsOnLocalFilesystemTask

    Raises an exception if `full_class_name` cannot be found.

    :param full_class_name: Fully-qualified name of a class as a string
    :return: A python class
    """
    module_name = ".".join(full_class_name.split(".")[0:-1])
    class_name = full_class_name.split(".")[-1]

    mod = importlib.import_module(module_name)
    return getattr(mod, class_name)
