Custom actions
==============

Custom actions are defined by the user in a Python module (.py file).

The user module name is provided as the keyword argument 'custom_actions_module' when instantiating
a Modbus simulator server object.

.. code-block::

    from pymodbus.server import ModbusSimulatorServer
    # ...
    server = ModbusSimulatorServer(
        # simulator server arguments ...
        custom_actions_module='my_custom_actions_module'
    )

The module file my_custom_actions.py in this case is located in the working directory i.e. the current directory from
which the program is executed.

Custom actions are executed as part of the server response to each and every client read and write request.
Some example use cases are:

- modify the register value on every register read request
- delay the server response on a register write request to test client timeout handling

.. note::
   Custom actions are executed at least once, but sometimes twice for each client request.
   This depends on the request function code.

   Some requests, such as write single register (function code 6),
   involve two operations and invoke the custom action twice; once when the register is written,
   and the a second time when the register is read back and returned in the response to the client.

   All function codes that perform a write operation and contain register values in the response
   will trigger a custom action twice. These include:

   * 05- write single coil
   * 06- write single register
   * 22- mask write register
   * 23- read/write multiple registers

User module
-----------

The user-provided module is a Python file with the following minimal contents

- a function with the prototype

.. code-block:: python

    def my_custom_action(registers, inx, cell, func_code, **kwargs):
        """My custom action
        :param registers: list of all register cells
        :param inx: index of the current request's register cell
        :param cell: current request's register cell
        :param func_code: function code of current request
        :param kwargs: additional keyword arguments
        """
        ...


- a dictionary named :code:`custom_actions_dict` that maps the function to a key

.. code-block:: python

    custom_actions_dict = {
    "custom_action_1": my_custom_action
    }

User module example
-------------------

The following is a custom action that delays the response to a write single register request (function code 6).

The write single register request is one in the subset of requests that invokes a write and a read operation in the
simulator. The custom action is triggered twice.

In order to prevent custom action business logic being executed twice, an attribute is defined outside the function
body- :code:`delay.action_performed = False`. This attribute is set to True when the custom action is triggered the
first time, and then set False the second time. The business logic is only executed the first time and the delay
in the response behaves as expected.

.. code-block:: python

    import time


    def delay(_registers, _inx, _cell, func_code, time_s):
        """Delay response to request
        :param _registers: list of all register cells (unused)
        :param _inx: index of the current request's register cell (unused)
        :param _cell: current request's register cell (unused)
        :param func_code: function code of current request
        :param time_s: response delay in seconds
        """

        """ A write single register operation triggers the custom action twice; once for the write operation,
        and again for the read operation in preparation of the response.
        """

        if delay.action_performed:
            delay.action_performed = False
            return

        if func_code == 0x06:  # write single register
            time.sleep(time_s)
            delay.action_performed = True


    delay.action_performed = False

    custom_actions_dict = {
        "write_hr_delay": delay,
    }

Simulator configuration
-----------------------

Custom actions can be associated with the relevant registers or register sets in the simulator's
JSON configuration file.

* The action is assigned to the register by introducing an ``action`` key and specifying the action name as the
  value. The action name is equal to the action's key entry in the custom actions module's ``custom_actions_dict``.
* Any additional arguments required by the custom action are defined by introducing the ``kwargs`` key with a
  keyword/value dictionary representing the custom action arguments.

Simulator configuration example
-------------------------------

Continuing from the example above, the following shows how to associate the user-provided ``write_hr_delay``
action with the 16-bit register address 2307. The ``time_s`` parameter is passed a value of 0.5.

.. code-block::

    "device_list": {
        ...
        "device_try": {
           ...
            "uint16": [
               ...
                {"addr":  2307,
                    "value": 43690,
                    "action": "write_hr_delay",
                    "kwargs": {"time_s":  0.5}
                }
                ...
            }
            ...
        }
        ...
    }
