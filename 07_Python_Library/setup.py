# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2022, MPL and LGPL HASOMED GmbH

# Alternatively, the contents of this file may be used under the terms
# of the GNU Lesser General Public License Version 3.0, as described below:
#
# This file is free software: you may copy, redistribute and/or modify
# it under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3.0 of the License, or (at your
# option) any later version.
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

from setuptools import setup, find_packages
import glob
import os
from io import FileIO
from pathlib import Path
import platform
import sys
import shutil

VERSION = '1.0.0'

package_data = {'': ['*.xml']}
package_data['sciencemode3'] = ['*.dll']
#if sys.platform.startswith('win'):  # windows
#    devel_roots = Path("../ScienceMode_Library").absolute()
#    if platform.architecture()[0] == '64bit':
#        architecture = 'x64'
#    else:
#        architecture = 'x86'
#    for devel_root in devel_roots:
#        dll_sources = glob.glob(os.sep.join([devel_root, 'lib', architecture, '*.dll']))
#        dll_dest = 'sciencemode'
#        for dll_source in dll_sources:
#            print('Copying {} to {}'.format(dll_source, dll_dest))
#            shutil.copy(dll_source, dll_dest)
#    package_data['sciencemode'] = ['*.dll']

setup(
    name='sciencemode3-cffi',
    packages=['sciencemode3'],
    package_data=package_data,
    version=VERSION,
    description='CFFI wrapper for SCIENCEMODE 3.x',
    author='Holger Nahrstaedt',
    author_email='holger.nahrstaedt@hasomed.de',
    license="MPL2",
    url='https://github.com/sciencemode/ScienceMode3',
    keywords=['sciencemode3', 'cffi'],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    setup_requires=['cffi>=1.0.0', 'pycparser>=2.14'],
    cffi_modules=[
        '{}:ffi'.format(os.sep.join(['sciencemode3', '_cffi.py'])),
    ],
    install_requires=['cffi>=1.0.0']
)