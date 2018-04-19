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
A module containing general helpers
"""
import difflib
import os
import random
import re
import string


def file_uri(path):
    """
    Returns `path` as a file URI

    Relative paths are resolved relative to the current working directory.

    :param path: A path string to convert
    :return: A file URI string (e.g. file:///usr)
    """
    if path.startswith("/"):
        return "file://" + path
    else:
        return "file://{cwd}/{path}".format(cwd=os.getcwd(), path=path)


def read_file_to_string(path):
    """
    Returns the contents of a file at ``path`` as a string.

    :param path: A path string
    :return: Contents of the file as a string
    :raises FileNotFoundError: If ``path`` does not exist
    :raises UnicodeDecodeError: If file does not contain UTF-8/ASCII text
    """
    with open(path, "r") as f:
        return f.read()


def write_str_to_file(path, s):
    """
    Write ``s`` to a file located at ``path``.

    :param path: Destination file path
    :param s: The string to write
    :raises FileExistsError if file exists
    """
    if os.path.exists(path):
        raise FileExistsError("{path}: already exists".format(path=path))

    with open(path, "w") as f:
        f.write(s)
        f.flush()


def merge(h1, h2):
    """
    Returns a new dictionary containing the key-value pairs of ``h1`` combined with the key-value pairs of ``h2``.

    Duplicate keys from ``h2`` overwrite keys from ``h1``.

    :param h1: A python dict
    :param h2: A python dict
    :return: A new python dict containing the merged key-value pairs
    """
    ret = {}
    ret.update(h1)
    ret.update(h2)
    return ret


def uri_subfolder(base, subfolder):
    """
    Returns a URI created by addin ``subfolder`` (a path) to the end of ``base`` (a URI).

    Assumes the protocol supports relative pathing. This function exists because python (stupidly) uses a whitelist for
    custom protocols (e.g. hdfs) when using urljoin. See: https://bugs.python.org/issue18828

    :param base: A URI
    :param subfolder: A path
    :return A URI
    """
    if base.endswith("/"):
        return base + subfolder
    else:
        return base + "/" + subfolder


def base36_str(desired_length=5):
    """
    Returns a randomly-generated base36 string with length ``desired_length``.

    :param desired_length: Length of the string to generate
    :return: A randomly-generated base36 string
    """
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(desired_length))


def bullet_point_list(str_list):
    return "".join(map(lambda s: "- " + s + "\n", str_list))


def try_get_val_or_key_error(dic, k):
    if k in dic:
        return dic[k]
    else:
        error_start = "{k}: not found".format(k=k)
        maybe_suggestions_msg = try_construct_suggestions_msg(dic, k)

        if maybe_suggestions_msg is not None:
            error_msg = error_start + ": " + maybe_suggestions_msg
        else:
            error_msg = error_start

        raise KeyError(error_msg)


def try_construct_suggestions_msg(dic, k):
    close_matches = difflib.get_close_matches(k, dic.keys())

    if len(close_matches) > 0:
        return "did you mean: {matches}?".format(matches=or_join(close_matches))
    else:
        return None


def or_join(strs):
    if len(strs) == 0:
        return ""
    elif len(strs) == 1:
        return strs[0]
    elif len(strs) == 2:
        return strs[0] + " or " + strs[1]
    else:
        first_els = "".join(map(lambda s: s + ", ", strs[0:-1]))
        last_el = strs[-1]
        return "{first_els}or {last_el}".format(first_els=first_els, last_el=last_el)


def to_camel_case(snake_case_str):
    """
    Returns `snake_case_str` (e.g. `some_str`) in CamelCase (e.g. `SomeStr`).

    :param snake_case_str: A string in `snake_case`
    :return: The string in `CamelCase`
    """
    els = [
        s[:1].upper() + s[1:]
        for s in snake_case_str.split("_")
    ]
    return "".join(els)


def to_snake_case(camel_case_str):
    """
    Returns `camel_case_str` (e.g. `SomeStr`) as snake_case (e.g. `some_str`)

    :param camel_case_str: A string in `CamelCase`
    :return: The string in `snake_case`
    """
    els = [
        el.lower()
        for el in re.findall("[a-zA-Z][^A-Z_]*", camel_case_str)
        if el != "_"
    ]
    return "_".join(els)
