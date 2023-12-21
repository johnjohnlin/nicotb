# Copyright (C) 2017-2019, Yu Sheng Lin, johnjohnlys@media.ee.ntu.edu.tw

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

import nicotb

class TestMainLoop:
    def test_event_fifo(self):
        # verify if the events are always handled in the order
        # they are pushed into the queue
        ev = [nicotb.CreateEvent() for i in range(3)]

        result = []
        def coro(ev):
            # wait for event and append the event to result
            yield ev
            result.append(ev)
            
        def main():
            # fork two events then trigger them in order
            for i in range(3):
                nicotb.Fork(coro(ev[i]))

            for i in range(3):
                nicotb.SignalEvent(ev[i])
            yield None

        nicotb.Fork(main())
        nicotb.MainLoop()

        assert result == ev

