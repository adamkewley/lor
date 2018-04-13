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
"""
Path resolution support.

LoR projects typically require building paths to files (e.g. input data, config). Those files *usually* reside in the
workspace, but *might* not: production deployments might need to override some of the workspace's files (e.g. for a
one-off, alternative workflow, performance test, etc.).

The definitions in this module add support for resolving paths from both "overlaid" workspace directories and the
workspace itself. Typically, clients will set "overlay dirs" at at LoR's command-line. This will set global
"overlay paths" in this module. Then, subsequent calls by workspace code to resolve a path will prioritize the overlays
where appropriate.

For example, if workspace code requests a config file:

.. code:: python

    import lor.path

    lor.path.resolve("etc/foo.yml")


And the LoR CLI was used:

    $ lor run --module workspace.tasks.foo FooTask --other-workspaces somedir/

Then this module will attempt to resolve "etc/foo.yml" against the `somedir/` overlay, followed by attempting to resolve
it against the current workspace.
"""
import os
import multipath
from lor import workspace

__overlay_paths = []


def get_overlay_paths():
    """
    Returns a list of overlay paths used application-wide.

    :return: A list of overlay path strings used application-wide.
    """
    return __overlay_paths


def _set_overlay_paths(new_overlay_paths):
    """
    Set the application-wide overlay paths.

    :param new_overlay_paths: A list of overlay paths. All paths *must* exist.
    :raises ValueError: If `overlay_paths` is not a list of path strings
    :raises FileNotFoundError: If any path in `overlay_paths` does not exist
    :raises NotADirectoryError: If any path in `overlay_paths` is not a directory
    """
    if not isinstance(new_overlay_paths, list):
        raise ValueError("{new_overlay_paths}: not a list: expecting a list of path strings".format(new_overlay_paths=str(new_overlay_paths)))
    for overlay_path in new_overlay_paths:
        if not isinstance(overlay_path, str):
            raise ValueError("{overlay_path}: is not a string: expecting an overlay path as a string".format(overlay_path=str(overlay_path)))
    for overlay_path in new_overlay_paths:
        if not os.path.exists(overlay_path):
            raise FileNotFoundError("{overlay_path}: no such directory: an overlay path argument must exist".format(overlay_path=overlay_path))
    for overlay_path in new_overlay_paths:
        if not os.path.isdir(overlay_path):
            raise NotADirectoryError("{overlay_path}: is not a directory: overlay paths must be directories".format(overlay_path=overlay_path))

    global __overlay_paths

    __overlay_paths = new_overlay_paths


def join(*paths):
    """
    Returns the top dir (i.e. top of overlay, or workspace dir) joined with *paths using os.path.join

    :param *paths: Path components to join onto the dir
    :return: A path resolved relative to the top dir
    :raises ValueError: If no overlay dirs are set *and* the workspace dir cannot be established
    """
    return multipath.join(__get_dirs(), *paths)


def __get_dirs():
    ws_path = workspace.get_path()

    if ws_path is None:
        return __overlay_paths
    else:
        return __overlay_paths + [ws_path]


def join_all(*paths):
    """
    Returns a list of path created by calling os.path.join on each overlay dir and the workspace with *paths.

    :param paths: Path components to join
    :return: A list of path strings
    """
    return multipath.join_all(__get_dirs(), *paths)


def resolve(*paths):
    """
    Joins `paths` onto each dir in overlay_dirs + workspace dir using `os.path.join` until one of the join results is
    found to exist and returns that existent result

    :param paths: Path components to join
    :return: The first path to be resolved that exists
    :raises ValueError: If no overlay dirs are set *and* the workspace dir cannot be established
    :raises FileNotFoundError: If no path could be resolved
    """
    return multipath.resolve(__get_dirs(), *paths)


def resolve_all(*paths):
    """
    Returns a list of paths created by joining paths onto each dir in overlay_dirs + the workspace using os.path.join
    and discarding all join results that do not exist.

    :param paths: Path components to join
    :return: A list of paths created by joining paths onto each dir in overlay_dirs + the workspace using os.path.join
    """
    return multipath.resolve_all(__get_dirs(), *paths)
