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
import glob
import logging
import os
import random
import string

import yaml
from luigi import Target

logger = logging.getLogger('etc-clusters')


def file_uri(local_path):
    if local_path.startswith("/"):
        return "file://%s" % local_path
    else:
        return "file://%s/%s" % (os.getcwd(), local_path)


def read_file_to_string(path):
    with open(path) as f:
        return f.read()


def read_non_blank_lines_in_file(path):
    with open(path) as file:
        for line in file:
            line = line.strip()
            if len(line) > 0:
                yield line


def read_yaml(path):
    with open(path, 'r') as f:
        return yaml.load(f)


def write_str_to_file(path, s):
    with open(path, "w") as f:
        f.write(s)
        f.flush()


def tree_map(h, key_mapper, leaf_mapper):
    """
    Perform a depth-first traversal of a hash, passing each
    key encountered to key_mapper and each value encountered to
    leaf_mapper.
    """

    if isinstance(h, dict):
        ret = {}

        for k, v in h.items():
            k2 = key_mapper(k)

            if isinstance(v, dict):
                v2 = tree_map(v, key_mapper, leaf_mapper)
            elif isinstance(v, list):
                v2 = list(map(lambda e: tree_map(e, key_mapper, leaf_mapper), v))
            else:
                v2 = leaf_mapper(v)

            ret[k2] = v2

        return ret
    else:
        return leaf_mapper(h)


def resolve_template_str(s, variables_h):
    """
    Substitute a template string (e.g. "$VAR1")
    """
    ret = s

    # Always substitute the longest match first.
    for varname in sorted(variables_h, key=len, reverse=True):
        varval = variables_h[varname]
        ret = ret.replace("$" + str(varname), str(varval))

    return ret


def merge(h1, h2):
    ret = {}
    ret.update(h1)
    ret.update(h2)
    return ret


def assert_file_exists(path, noun="file"):
    if not os.path.exists(path):
        error_msg = "Cannot find {noun} at {path}".format(noun=noun, path=path)
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)


def uri_subfolder(base, subfolder):
    """
    Join a subfolder onto a URI. This function exists because python (stupidly)
    uses a whitelist for custom protocols (e.g. hdfs) when using urljoin.
    """
    if base.endswith("/"):
        return base + subfolder
    else:
        return base + "/" + subfolder


def base36_str(l=5):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(l))


def flatten(lst):
    ret = []
    for x in lst:
        if isinstance(x, list):
            for y in x:
                ret.append(y)
        else:
            ret.append(x)
    return ret


def task_input_merge(task_input):
    if isinstance(task_input, Target):
        return task_input
    elif isinstance(task_input, dict):
        ret = {}
        for k, v in task_input.items():
            mapped_v = task_input_merge(v)
            if isinstance(mapped_v, dict):
                for k2, v2 in mapped_v.items():
                    ret_key = "{k}_{k2}".format(k=k, k2=k2)
                    ret[ret_key] = v2
            else:
                ret[k] = mapped_v
        return ret
    else:
        raise RuntimeError("{type}: Cannot be merged into other task outputs".format(type=type(task_input)))


def map_vals(f, d):
    return dict(map(lambda t: (t[0], f(t[1])), d.items()))


def find_newest_file_in_dir(glob_pattern):
    all_files = glob.glob(glob_pattern)
    return max(all_files, key=os.path.getctime)


def subdirs_in(path):
    dir_names = next(os.walk(path))[1]
    return map(lambda dir_name: os.path.join(path, dir_name), dir_names)


def with_trailing_slash(s):
    if s.endswith("/"):
        return s
    else:
        return s + "/"


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
