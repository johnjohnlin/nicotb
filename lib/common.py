# Copyright (C) 2017,2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

# This file is part of Nicotb.

# Nicotb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Nicotb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Nicotb.  If not, see <http://www.gnu.org/licenses/>.
from os import getenv
import numpy as np

SUPPORT_NP_TYPES = [np.int8, np.int16, np.int32, np.uint8, np.uint16, np.uint32,]
TOP_PREFIX = getenv("TOPMODULE")
if TOP_PREFIX is None:
	TOP_PREFIX = str()
else:
	TOP_PREFIX += "."
NICOTB_MODE = getenv("NICOTB_MODE")
if NICOTB_MODE == "VPI":
	from bridge_vpi import BindBus, ReadBus, WriteBus, BindEvent
	COSIM = True
elif NICOTB_MODE == "VERILATOR":
	from bridge_verilator import BindBus, ReadBus, WriteBus, BindEvent
	COSIM = True
else:
	COSIM = False
