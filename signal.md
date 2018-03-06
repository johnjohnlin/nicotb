---
layout: page
title: "Nicotb Document"
---

# Python-Verilog Interface of Nicotb

Nicotb provides the Python-Verilog connection through these structures:

* `Signal`,
	* A verilog logic/wire/reg array like `logic [31:0] some_signal [3];`.
* `Bus`, and
	* A group of one or more Signals which is the smallest write/read unit in Nicotb.
* `Event`
	* When event happens, the Verilog part triggers the event.
	  Usually only clock and reset are required for a single clock domain verification.
	  They can be constructed in Python without being associated with a Verilog event.

## Signal

A `Signal` corresponds to a Verilog array as show this table,
but you don\'t have to construct `Signal` explicitly.
Find out more information later in the `Bus` part.

|       Verilog type          | Numpy array shape |
|-----------------------------|-------------------|
| `logic a;`                  | `(1,)`            |
| `logic [3:0] a;`            | `(1,)`            |
| `logic [3:0] a [1];`        | `(1,)`            |
| `logic [3:0] a [10];`       | `(10,)`           |
| `logic [3:0] a [3][5];`     | `(3,5,)`          |
| `logic [3:0] a [1][5];`     | `(1,5,)`          |

Owing to some limitations of VPI, only 1/2/4B signed/unsigned integer signal types are supported as Numpy types.
Narrower signal can be holded by a wider one, and usually using the default 4B signed is enough.

You can access the signal value by calling `Signal.Write` and `Signal.Read`,
and the Verilog wire values are mapped to two Numpy arrays `Signal.value` and `Signal.x`.
It follows the standard coding of the 4-Value of Verilog,
and `(value/x) = (0b0011/0b0101)` stands for `4'b01xz`.
Since we implement the `value` and `x` with Python setter and getter,
codes like `Signal.value = 30` or `Signal.value = [1,2,3,]` work fine without losing the reference to the Numpy array.

## Bus

A `Bus` is a collection of `Signal`s,
and `Bus.Read`/`Write` can transfer all signals to/from Verilog.
It can be constructed by the `CreateBus` API.
This function call accepts a tuple of signal description.

```python
bus = CreateBus((
	# Top level signal logic wire_name1;
	("", "wire_name1"),
	# Note that this one different.
	# Even if they both construct Numpy array of shape = (1,).
	("", "wire_name2", (1,)),
	# A signal in some.hierarchy, logic [5:0] wire_name1 [2][2];
	# The default is shape and type are tuple(), np.int32.
	("some.hierarchy", "wire_name1", (2,2) , np.int16,),
))
```

There are some shortcuts, for example, `None` can be used if the hierarchy are repeated.

```python
bus = CreateBus((
	("us", "nico"),
	("us", "maki"),
	("us", "umi"),
	("us", "kotori"),
))
# This is equivalent.
bus = CreateBus((
	("us", "nico"),
	(None, "maki"),
	(None, "umi"),
	(None, "kotori"),
))
```

Toplevel signals can be used without writing the hierarchy.

```python
bus = CreateBus((
	("", "nico"),
))
# This is equivalent.
# Be aware that ("nico",) is a tuple while ("nico") is not in Python.
bus = CreateBus((
	("nico",),
))
```

Also, there is a `CreateBuses` utility function that accepts and returns a list.

The signal can be accessed by index `Bus[99]` or by name `Bus.nico`
(in the latter case, you must avoid using the Python keyword and duplicated names).
Therefore, you can modify the value by either using `Bus[99].value`, `Bus.nico.value`, `Bus.values[99]`, or `Bus.values.nico`.
If the bus only has one signal, `Bus.value` also works fine.
All of this API returns a Numpy array, and you should not assign to it,
otherwise, mostly you will update a tuple, which is invalid in Python.
The correct way to modify the array is to update the content of Numpy array,
and we show some of them here:

```python
numpy.copyto(arr, 25251)
numpy.copyto(arr, [25251,])
arr[:] = 25251
arr[10, :] = [25251, 12345, 65535]
```

## Event
### Verilog Event

An event can be create by the `CreateEvent` in the similar way with `CreateBus`.
However, it should have a integer scalar type and be under the toplevel,
so the only way to create an event is `CreateEvent("clock")`.
Also, there is a list version `CreateEvents`.
You can use these functions in this way:

```python
x = CreateEvent("x");
yield x
print("100ns passed")
yield x
print("10ns passed")
```

```verilog
integer x;
initial begin
    #100
    $NicotbTriggerEvent(x);
    #10
    $NicotbTriggerEvent(x);
end
```

In current version, events are simply integers,
so if you print the type of an event, you get an `int` type.
Therefore, both

```python
x = CreateEvent("x");
for i in range(100):
    yield x
```

and

```python
# Note, yield from is from Python 3.3
from itertools import repeat
x = CreateEvent("x");
yield from repeat(x, 100)
```

work exactly the same.

For the Verilog part, we can use the macro `PosIf` and `Pos` to simplify creating events in Verilog,
and most of the time you just need them.

```verilog
`PosIf(clock_python_name, verilog_clock_wire, verilog_reset_wire)
```
In the Python part, you just write

```python
clk = CreateEvent("clock_python_name")
for i in range(100):
    yield clk
```

for waiting 100 cycles.

### Indepedent Event
An event can be created without binding to a Verilog one,
and you just call `CreateBus` without argument.

```python
xx = CreateEvent()
TriggerEvent(xx)
TriggerEvent(xx)
```

### Implicit Event
Events are created automatically if you use synchronization primitives such as `Lock`.
