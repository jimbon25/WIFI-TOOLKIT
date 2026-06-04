import os
import shlex
import subprocess
import logging
from evillimiter.console.io import IO

logger = logging.getLogger(__name__)

# Use proper context managers for file operations
_DEVNULL = subprocess.DEVNULL


def execute(command, root=True):
    """
    Execute a command safely without shell=True vulnerability.
    
    Args:
        command: Command string to execute
        root: Whether to use sudo
        
    Returns:
        Return code of the command
    """
    try:
        cmd_list = shlex.split(command)
        if root:
            cmd_list = ['sudo'] + cmd_list
        
        return subprocess.call(cmd_list, shell=False)
    except FileNotFoundError as e:
        IO.error(f'Command not found: {e}')
        return -1
    except Exception as e:
        IO.error(f'Error executing command: {e}')
        return -1


def execute_suppressed(command, root=True):
    """Execute command with output suppressed."""
    try:
        cmd_list = shlex.split(command)
        if root:
            cmd_list = ['sudo'] + cmd_list
        
        return subprocess.call(cmd_list, shell=False, stdout=_DEVNULL, stderr=_DEVNULL)
    except FileNotFoundError as e:
        logger.error(f'Command not found: {e}')
        return -1
    except Exception as e:
        logger.error(f'Error executing command: {e}')
        return -1


def output(command, root=True):
    """Execute command and return stdout."""
    try:
        cmd_list = shlex.split(command)
        if root:
            cmd_list = ['sudo'] + cmd_list
        
        result = subprocess.check_output(cmd_list, shell=False, stderr=subprocess.PIPE)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        IO.error(f'Command failed: {e}')
        return ''
    except FileNotFoundError as e:
        IO.error(f'Command not found: {e}')
        return ''
    except Exception as e:
        IO.error(f'Error executing command: {e}')
        return ''


def output_suppressed(command, root=True):
    """Execute command and return stdout, suppressing stderr."""
    try:
        cmd_list = shlex.split(command)
        if root:
            cmd_list = ['sudo'] + cmd_list
        
        result = subprocess.check_output(cmd_list, shell=False, stderr=_DEVNULL)
        return result.decode('utf-8')
    except subprocess.CalledProcessError:
        return ''
    except FileNotFoundError:
        return ''
    except Exception as e:
        logger.error(f'Error executing command: {e}')
        return ''


def locate_bin(name):
    """Locate a binary in the system PATH."""
    try:
        which_output = output_suppressed(f'which {name}')
        if which_output:
            return which_output.replace('\n', '')
        else:
            IO.error(f'missing util: {name}, check your PATH')
            return None
    except Exception as e:
        IO.error(f'Error locating binary {name}: {e}')
        return None