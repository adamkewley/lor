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
File/directory generation support

Generators help with LoR's "convention over configuration" approach by providing generators for the most common files
users are likely to need (e.g. a Luigi task). Using generators, clients are more likely to write standard projects with
a standard layout rather than create their own. This should hopefully standardize LoR projects enough to make it easier
for devs to work together on LoR projects.

This module contains helpers for writing Generators. Generators are classes that have a command-line interface and, when
ran, generate files in the output dir (usually, a workspace). LoR generators have support for:

- Writing files with CLI feedback
- Rendering Jinda2 templates
- Running other generators
- Running executable files (e.g. install scripts)
"""
