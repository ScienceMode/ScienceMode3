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

from cffi import FFI
from subprocess import check_output
import re
import os
import pycparser
import json
import itertools
import platform
import sys
from pycparser import c_ast
from pycparser.c_generator import CGenerator

INCLUDE_PATTERN = re.compile(r'(-I)?(.*ScienceMode)')
DEFINE_PATTERN = re.compile(r'^#define\s+(\w+)\s+\(?([\w<|.]+)\)?', re.M)
DEFINE_BLACKLIST = {
    'main',
    }

devel_root = os.path.abspath("smpt")
include_dir = os.path.join(devel_root, "include")


smpt_lib_path = os.path.abspath('./smpt/lib')
smpt_lib = os.path.join(smpt_lib_path, 'libsmpt.lib')

smpt_include_path1 = os.path.join(include_dir, "general")
smpt_include_path2 = os.path.join(include_dir, "low-level")
smpt_include_path3 = os.path.join(include_dir, "mid-level")

# define GCC specific compiler extensions away
DEFINE_ARGS = [
    '-D_WIN32',
    '-D__attribute__(x)=',
    '-D__inline=',
    '-D__restrict=',
    '-D__extension__=',
    '-D__GNUC_VA_LIST=',
    '-D__inline__=',
    '-D__forceinline=',
    '-D__volatile__=',
    '-D__MINGW_NOTHROW=',
    '-D__nothrow__=',
    '-DCRTIMP=',
    '-DSDL_FORCE_INLINE=',
    '-DDOXYGEN_SHOULD_IGNORE_THIS=',
    '-D_PROCESS_H_=',
    '-U__GNUC__',
    '-Ui386',
    '-U__i386__',
    '-U__MINGW32__',
    '-DNT_INCLUDED',
    '-D_MSC_VER=1900',
    '-L'+smpt_lib_path,
    '-Iutils/fake_libc_include',
    '-Iutils/fake_windows_include',
    '-I'+smpt_include_path1,
    '-I'+smpt_include_path2,
    '-I'+smpt_include_path3,
]

FUNCTION_BLACKLIST = {

}

VARIADIC_ARG_PATTERN = re.compile(r'va_list \w+')
ARRAY_SIZEOF_PATTERN = re.compile(r'\[[^\]]*sizeof[^\]]*]')

HEADERS = [
    'general/smpt_definitions_data_types.h',
    'general/smpt_definitions.h',
    'general/smpt_messages.h',
    'general/smpt_packet_number_generator.h',
    'low-level/smpt_ll_definitions.h',
    'low-level/smpt_ll_definitions_data_types.h',
    'mid-level/smpt_ml_definitions.h',
    'mid-level/smpt_ml_definitions_data_types.h',
]

ROOT_HEADERS = [
    'general/smpt_client.h',
    'low-level/smpt_ll_client.h',
    'mid-level/smpt_ml_client.h',
]



class Collector(c_ast.NodeVisitor):

    def __init__(self):
        self.generator = CGenerator()
        self.typedecls = []
        self.functions = []

    def process_typedecl(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            typedecl = '{};'.format(self.generator.visit(node))
            typedecl = ARRAY_SIZEOF_PATTERN.sub('[...]', typedecl)
            if typedecl not in self.typedecls:
                self.typedecls.append(typedecl)

    def sanitize_enum(self, enum):
        for name, enumeratorlist in enum.children():
            for name, enumerator in enumeratorlist.children():
                enumerator.value = c_ast.Constant('dummy', '...')
        return enum

    def visit_Typedef(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            if ((isinstance(node.type, c_ast.TypeDecl) and
                 isinstance(node.type.type, c_ast.Enum))):
                self.sanitize_enum(node.type.type)
            self.process_typedecl(node)

    def visit_Union(self, node):
        self.process_typedecl(node)

    def visit_Struct(self, node):
        self.process_typedecl(node)

    def visit_Enum(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            node = self.sanitize_enum(node)
            self.process_typedecl(node)

    def visit_FuncDecl(self, node):
        coord = os.path.abspath(node.coord.file)
        if node.coord is None or coord.find(include_dir) != -1:
            if isinstance(node.type, c_ast.PtrDecl):
                function_name = node.type.type.declname
            else:
                function_name = node.type.declname
            if function_name in FUNCTION_BLACKLIST:
                return
            decl = '{};'.format(self.generator.visit(node))
            decl = VARIADIC_ARG_PATTERN.sub('...', decl)
            if decl not in self.functions:
                self.functions.append(decl)


ffi = FFI()




ffi.set_source(
 "sciencemode3._sciencemode",
 ('\n').join('#include "%s"' % header for header in ROOT_HEADERS),
 include_dirs = [include_dir, smpt_include_path1, smpt_include_path2, smpt_include_path3],
 libraries = ['libsmpt'],
 library_dirs = [smpt_lib_path],
 extra_objects = [smpt_lib],
)



pycparser_args = {
    'use_cpp': True,
    'cpp_args': DEFINE_ARGS
}
if sys.platform.startswith('win'):  #windows
    mingw_path = os.getenv('MINGW_PATH', default='C:\\Qt\\Tools\\mingw530_32')
    pycparser_args['cpp_path'] = '{}\\bin\\cpp.exe'.format(mingw_path)

collector = Collector()
for header in ROOT_HEADERS:
    ast = pycparser.parse_file(os.sep.join([include_dir, header]), **pycparser_args)
    collector.visit(ast)

defines = set()
for header_path in HEADERS:
    with open(os.sep.join([include_dir, header_path]), 'r') as header_file:
        header = header_file.read()
        for match in DEFINE_PATTERN.finditer(header):
            if match.group(1) in DEFINE_BLACKLIST or match.group(1) in collector.typedecls or match.group(1) in collector.functions:
                continue
            try:
                int(match.group(2), 0)
                defines.add('#define {} {}'.format(match.group(1),
                                                   match.group(2)))
            except:
                defines.add('#define {} ...'.format(match.group(1)))

print('Processing {} defines, {} types, {} functions'.format(
    len(defines),
    len(collector.typedecls),
    len(collector.functions)
))

cdef = '\n'.join(itertools.chain(*[
    defines,
    collector.typedecls,
    collector.functions
]))

cdef = cdef.replace('[Smpt_Length_Max_Packet_Size]', '[1200]')
cdef = cdef.replace('[Smpt_Length_Max_Packet_Size]', '[1200]')
cdef = cdef.replace('[Smpt_Length_Packet_Input_Buffer_Rows]', '[100]')
cdef = cdef.replace('[Smpt_Length_Packet_Input_Buffer_Rows * Smpt_Length_Max_Packet_Size]', '[120000]')
cdef = cdef.replace('[Smpt_Length_Serial_Port_Chars]','[256]')
cdef = cdef.replace('[Smpt_Length_Number_Of_Acks]', '[100]')
cdef = cdef.replace('[Smpt_Length_Device_Id]', '[10]')
cdef = cdef.replace('[Smpt_Length_Points]', '[16]')
cdef = cdef.replace('[Smpt_Length_Number_Of_Channels]', '[4]')
cdef = cdef.replace('[Smpt_Length_Number_Of_Switches]', '[512]')
cdef = cdef.replace('[Smpt_Length_Demux_Config]', '[64]')
cdef = cdef.replace('[Smpt_Length_Demux_Id]', '[50]')


ffi.cdef(cdef)

if False:
    file = open('sciencemode3.cdef', 'w')
    file.write(cdef)
    file.close()
