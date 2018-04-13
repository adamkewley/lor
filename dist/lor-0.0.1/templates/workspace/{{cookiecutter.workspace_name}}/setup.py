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
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open('README.md') as f:
    readme = f.read()

with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

setup(
    name='{{cookiecutter.workspace_name}}',
    version='0.0.1-SNAPSHOT',
    description="{{cookiecutter.description}}",
    long_description=readme,
    author='{{cookiecutter.author}}',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=all_reqs,
)