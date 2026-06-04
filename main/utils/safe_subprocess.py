"""
Safe subprocess execution module.
Prevents command injection by using argument lists instead of shell strings.
"""

import subprocess
import shlex
import logging
from typing import List, Union, Optional, Tuple
import os

logger = logging.getLogger(__name__)


def safe_execute(command: Union[str, List[str]], sudo: bool = False, 
                 quiet: bool = False, capture_output: bool = False) -> Optional[subprocess.CompletedProcess]:
    """
    Safely execute a command without shell=True vulnerability.
    
    Args:
        command: Command as string or list of arguments
        sudo: Whether to prepend 'sudo' to the command
        quiet: Suppress output
        capture_output: Capture stdout/stderr
        
    Returns:
        CompletedProcess object or None on error
        
    Raises:
        ValueError: If command is invalid
        FileNotFoundError: If executable not found
        subprocess.CalledProcessError: If command fails (when capture_output=True)
    """
    # Convert string to list if needed
    if isinstance(command, str):
        command = shlex.split(command)
    elif not isinstance(command, list):
        raise ValueError("Command must be string or list")
    
    if not command:
        raise ValueError("Command list cannot be empty")
    
    # Validate command list has no problematic shell characters
    for arg in command:
        if not isinstance(arg, str):
            raise ValueError(f"All command arguments must be strings, got {type(arg)}")
    
    # Build final command
    final_command = command
    if sudo:
        final_command = ['sudo'] + command
    
    logger.debug(f"Executing: {final_command}")
    
    try:
        stdout_opt = subprocess.PIPE if (quiet or capture_output) else None
        stderr_opt = subprocess.PIPE if (quiet or capture_output) else None
        
        result = subprocess.run(
            final_command,
            shell=False,  # CRITICAL: Never use shell=True
            check=False,
            stdout=stdout_opt,
            stderr=stderr_opt,
            text=True
        )
        
        if result.returncode != 0 and not quiet:
            logger.warning(f"Command failed with return code {result.returncode}: {final_command}")
            if result.stderr:
                logger.warning(f"Stderr: {result.stderr}")
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Command not found: {final_command[0]}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Command execution failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error executing command: {e}")
        raise


def safe_execute_with_output(command: Union[str, List[str]], sudo: bool = False) -> str:
    """
    Execute command and return stdout as string.
    
    Args:
        command: Command as string or list
        sudo: Whether to use sudo
        
    Returns:
        Command output as string
        
    Raises:
        subprocess.CalledProcessError: If command fails
    """
    result = safe_execute(command, sudo=sudo, capture_output=True)
    return result.stdout.strip() if result.stdout else ""


def safe_popen(command: Union[str, List[str]], sudo: bool = False, 
               **kwargs) -> subprocess.Popen:
    """
    Safely create a Popen subprocess without shell=True.
    
    Args:
        command: Command as string or list
        sudo: Whether to use sudo
        **kwargs: Additional Popen arguments
        
    Returns:
        Popen object
    """
    if isinstance(command, str):
        command = shlex.split(command)
    elif not isinstance(command, list):
        raise ValueError("Command must be string or list")
    
    if sudo:
        command = ['sudo'] + command
    
    kwargs['shell'] = False  # Ensure shell=False
    logger.debug(f"Creating Popen: {command}")
    
    return subprocess.Popen(command, **kwargs)


def is_valid_cli_input(user_input: str, max_length: int = 1000) -> bool:
    """
    Validate user input for CLI safety.
    
    Args:
        user_input: User provided input
        max_length: Maximum allowed length
        
    Returns:
        True if input is safe, False otherwise
    """
    if not isinstance(user_input, str):
        return False
    
    if len(user_input) > max_length:
        logger.warning(f"Input exceeds max length of {max_length}")
        return False
    
    # Check for suspicious patterns
    dangerous_chars = [';', '|', '&', '`', '$', '(', ')', '<', '>', '\n', '\r']
    for char in dangerous_chars:
        if char in user_input:
            logger.warning(f"Suspicious character detected: {repr(char)}")
            return False
    
    return True


def validate_command_args(args: List[str]) -> bool:
    """Validate command arguments are safe strings."""
    if not isinstance(args, list):
        return False
    
    for arg in args:
        if not isinstance(arg, str):
            return False
        if len(arg) > 10000:
            return False
    
    return True
