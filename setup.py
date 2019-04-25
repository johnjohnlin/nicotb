#!/usr/bin/env python3
from distutils.core import setup, Extension
from numpy import get_include
from glob import glob

ext_args = {
	'libraries': ['glog'],
	'extra_compile_args': ['--std=c++11'],
	'include_dirs': [get_include()],
	'define_macros': [
		('NDEBUG', None),
		('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
	]
}
setup(
	name='Nicotb',
	version='0.5',
#	description='Python Distribution Utilities',
	author='Yu-Sheng Lin',
	author_email='johnjohnlys@media.ee.ntu.edu.tw',
	packages=['nicotb', 'nicotb.protocol'],
	package_dir={
		'nicotb': 'lib',
	},
	ext_modules=[
		Extension(
			'nicotb.bridge_vpi',
			['lib/cpp/nicotb_python.cpp', 'lib/cpp/nicotb_vpi.cpp'],
			**ext_args,
		),
		Extension(
			'nicotb.bridge_verilator',
			['lib/cpp/nicotb_python.cpp', 'lib/cpp/nicotb_verilator.cpp'],
			**ext_args,
		),
	],
	package_data={'nicotb': ['verilog/*']},
)
