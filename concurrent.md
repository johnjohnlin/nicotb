---
layout: default
title: Concurrency
---

# Support Concurrency in Nicotb

## Introdution

In hardware simulation asynchronized or concurrent execution are very important,
since modules in a hardware executes in parallel.
For example, we commonly use `initial` blocks, `fork` and `join` in a SystemVerilog testbench;
in SystemC, `SC_THREAD`, `SC_METHOD` are used to support concurrency.

The asynchronized or concurrent model appears in many modern languages JS, Golang;
Python 3.5-3.6 introduces `asyncio` and *co-routine*, which is useful for IO-heavy codes
However, the built-in API provides less control on the scheduling,
and we find that it could be hard to use it for SystemVerilog co-simulation,
so we choose the old friend, the **generator**, as the basis in Nicotb.
*Generator* is the very primary form of co-routine, it require much text to explain,
but you can find lots of tutorial on the web about it and I will just skip it.

## Simulate Concurreny with Generators

In the following code segment,
we show an very simple example that two *generators* are scheduled in the `main_loop()` function,
as if two thread are executed in parallel, and the they are also synchronized by the `yield`.
`yield`, even if `f` and `g` is actually executed in sequential.

```python
def f():
    for i in range(5):
        print("Function f, {}".format(i))
        yield
    print("Function f finished")

def g():
    for i in range(3):
        print("Function g, {}".format(i))
        yield
    print("Function g finished")

def main_loop(threads):
    from itertools import zip_longest
    for dummy in zip_longest(*threads):
        pass

main_loop([f(), g()])
# Note: this is wrong
# main_loop([f, g])
```

This output is:

```text
Function f, 0
Function g, 0
Function f, 1
Function g, 1
Function f, 2
Function g, 2
Function f, 3
Function g finished
Function f, 4
Function f finished
```

## Events in Nicotb

*Events* is one of the most important parts in concurrency,
and it also exists as a built-in type in SystemVerilog.
Actually, implemnting *events* can be very simple,
an *event* can be as simple as an integer *index*,
and the new code should `yield` the *event index* for waiting for the *event* to be triggered.
We simplify the problem that we know the number of *events*, say 4, in advance:

```python
def g():
    yield 2
    yield 0
    yield 3

def main_loop(threads, n_event=0):
    # ...

main_loop([g()], 4)
```

How to implement the event-based scheduling?
In the previous section we use the built-in `zip_iterator` as a simpler scheduler,
For supporting *events*, we must implement our own scheduler.
Specifically, we maintain a *queue* to hold the pending *events* and a *list* to store which *generator* is waiting for the *event* to be triggered.

The logic of the scheduler is:

1. As long as the *queue* is not empty, pop the *event index* and execute the waiting *generators*.
1. If the *generator* doesn't terminate,
   then it yields an *event index* it's waiting for and should be added to the correspoinding *event index*.
1. Whenever an *event* is triggered, it is pushed to the *queue*, and is scheduled in the next time step.

```python
def f():
    print("f wait")       # T0
    yield 0               # wait on event 0
    print("f trigger 1")  # T1
    trigger_event(1)
    print("f finish")     # T2

def g():
    print("g trigger 0")  # T0
    trigger_event(0)
    yield 1               # wait on event 1
    print("g finish")     # T2

def trigger_event(i):
    event_pending.append(i)

def schedule(threads):
    for t in threads:
        try:
            wait_on_idx = next(t)
            event_queue[wait_on_idx].append(t)
        except StopIteration:
            pass

# NOTE: If fact we should use a deque instead of the list.
event_pending = list()
event_queue = None
def main_loop(threads, n_event):
    global event_pending, event_queue
    event_queue = [list() for dummy in range(n_event)]
    schedule(threads)
    i = 0
    while event_pending:
        print("==== Time step {} ====".format(i))
        # Pop an event from front
        event_idx = event_pending[0]
        event_pending = event_pending[1:]
        this_event_threads = event_queue[event_idx]
        event_queue[event_idx] = list()
        schedule(this_event_threads)

main_loop([g(), f()], 2)
```
Executing this code, we obtain this output.

```text
f wait
g trigger 0
==== Time step 0 ====
f trigger 1
f finish
==== Time step 1 ====
g finish
```

## Race Condition
Note that if we change `main_loop([f(), g()], 2)` into `main_loop([g(), f()], 2)`,
then the output is slightly different:

```text
g trigger 0
f wait
==== Time step 0 ====
f trigger 1
f finish
==== Time step 1 ====
g finish
```

This is not a bug, and this is common in asynchronize programming.
Simultaneous threads synchronized by the same events are not guaranteed to be executed in a fixed order.
As long as the time steps are not mixed up, the results are valid.

### dont\_initialize in SystemC
A small note is that, some lines are print before "Time step 0".
If you are familiar with SystemC, you can use a `dont_initialize()` to prevent this before `sc_start()`.
This can be implemented by adding a pseudo-event called the initizlized event,
we can allocate one extra event more than the number the user requests,
and then `yield -1` force the thread to wait on that events.
(Note: we somewhat abuse that `x[-1]` gives the last element in Python.)

```python
def main_loop(threads, n_event):
    global event_pending, event_queue
    event_queue = [list() for dummy in range(n_event+1)]
    schedule(threads)
    trigger_event(-1)
    i = 0
    while event_pending:
```

We don't need to modify anything else to support SystemC-like `dont_initialize`.
Adding `yield -1` at the first line of `f` and `g` gives us:

```
==== Time step 0 ====
f wait
g trigger 0
==== Time step 1 ====
f trigger 1
f finish
==== Time step 2 ====
g finish
```

## Nested Events
Nested events are supported directly with `yield from` added in Python 3.3,
or you can use the older equivalent for-loop.

```python
def f_nest():
    for i in range(10):
        print(i)
        yield 0

def f():
    for n in f_nest():
        yield n
    # If you are using Python 3.3+, then this will be better.
    # They are equivalent.
    # yield from f_nest()

def g():
    for n in f_nest():
        trigger_event(0)

main_loop([f(), g()], 1)
```

Wait! Running this code, you will get

```text
TypeError: 'NoneType' object is not an iterator
```

exception.
This is because that `g` doesn't include any `yield` and thus is not a generator.
But what event should we wait?
The finish of initialization phase could be a good choice, that is,
to add a `yield -1` at the top of `g`.
This is reasonable since if the initialization isn't done yet,
then the generators aren't waiting on the correct event index,
which could easily give wrong results.

## Summing up

In the production code of Nicotb, it is necessary add more funcionalities like:

* Allocate events dynamically,
* Add `Fork`, `Join` and basic synchronization primitives and
* Informative error messages.

But most of them are software engineering tasks.
