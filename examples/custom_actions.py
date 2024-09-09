""" Simulator custom actions example module.

See simulator.py for example usage.

"""
import time


def delay(_registers, _inx, _cell, func_code, time_s):
    """Delay reply to write single register function code"""
    if delay.action_performed:
        delay.action_performed = False
        return

    if func_code == 0x06:  # write single register
        time.sleep(time_s)
        delay.action_performed = True


delay.action_performed = False


def read_hr_always_return_value(registers, inx, _cell, func_code, value):
    """Always return user-supplied value to read holding register function code"""
    if func_code == 0x03:  # read holding register
        registers[inx].value = value
    return


custom_actions_dict = {
    "write_hr_delay": delay,
    "read_hr_always_return_value": read_hr_always_return_value,
}
