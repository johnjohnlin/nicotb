#!/usr/bin/env python3
from distutils.core import setup, Extension
from numpy import get_include
from glob import glob

ext_args = {
	'libraries': ['glog'],
	'extra_compile_args': ['--std=c++11'],
	'include_dirs': [get_include()],
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
	# NOTE
	# While we build these libraries, it is not used from standalone execution.
	# In other words, you should not import nicotb.bridge_xxx explicitly in any of your code.
	# Instead, these modules are registered in without the "nicotb." prefix in Nicotb::Python::Init()
	# of nicotb_python.cpp by PyImport_AppendInittab("bridge_xxx", ...).
	# As you can see in nicotb/common.py
	#     from bridge_xxx import BindBus, ReadBus, WriteBus, BindEvent
	# , we import the bridge modules without the "nicotb." prefix.
	ext_modules=[
		Extension(
			'nicotb.bridge_vpi',
			['lib/cpp/nicotb_python.cpp', 'lib/cpp/nicotb_vpi.cpp'],
			define_macros=[
				('NDEBUG', None),
				('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
				('NICOTB_MODULE_NAME', '"bridge_vpi"'),
			],
			**ext_args,
		),
		Extension(
			'nicotb.bridge_verilator',
			['lib/cpp/nicotb_python.cpp', 'lib/cpp/nicotb_verilator.cpp'],
			define_macros=[
				('NDEBUG', None),
				('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
				('NICOTB_MODULE_NAME', '"bridge_verilator"'),
			],
			**ext_args,
		),
	],
	package_data={'nicotb': ['verilog/*', 'cpp/*.h']},
)
