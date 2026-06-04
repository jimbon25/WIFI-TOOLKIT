"""
Dependency Injection (DI) Framework for WiFi-Tool.
Provides inversion of control for cleaner, more testable architecture.

This module enables:
- Service registration and retrieval
- Singleton and transient lifetime management
- Constructor injection
- Interface-based dependency resolution
- Easy testing via mock injection
"""

from typing import Dict, Any, Callable, Type, Optional, Set
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class CircularDependencyError(Exception):
    """Raised when circular dependency detected."""
    pass


class ServiceNotFoundError(Exception):
    """Raised when requested service not registered."""
    pass


class LifetimeError(Exception):
    """Raised when service lifetime is invalid."""
    pass


class ServiceContainer:
    """
    Main dependency injection container.
    Manages service registration, resolution, and lifecycle.
    """
    
    SINGLETON = 'singleton'
    TRANSIENT = 'transient'
    SCOPED = 'scoped'
    
    def __init__(self):
        """Initialize empty service container."""
        self._services: Dict[str, Dict[str, Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._resolution_stack: Set[str] = set()
    
    def register(
        self,
        service_name: str,
        factory: Callable,
        lifetime: str = SINGLETON,
        dependencies: Optional[list] = None
    ) -> None:
        """
        Register a service in the container.
        
        Args:
            service_name: Unique name for the service
            factory: Callable that creates the service
            lifetime: 'singleton', 'transient', or 'scoped'
            dependencies: List of service names this depends on
            
        Raises:
            LifetimeError: If lifetime is invalid
        """
        if lifetime not in (self.SINGLETON, self.TRANSIENT, self.SCOPED):
            raise LifetimeError(f"Invalid lifetime: {lifetime}")
        
        self._services[service_name] = {
            'factory': factory,
            'lifetime': lifetime,
            'dependencies': dependencies or [],
        }
        
        logger.debug(f"Registered service: {service_name} (lifetime: {lifetime})")
    
    def register_instance(self, service_name: str, instance: Any) -> None:
        """Register a pre-created singleton instance."""
        self._singletons[service_name] = instance
        self._services[service_name] = {
            'factory': lambda: instance,
            'lifetime': self.SINGLETON,
            'dependencies': [],
        }
        logger.debug(f"Registered instance: {service_name}")
    
    def register_class(
        self,
        service_name: str,
        cls: Type,
        lifetime: str = SINGLETON,
        **constructor_args
    ) -> None:
        """
        Register a class as a service.
        
        Args:
            service_name: Service name
            cls: Class to instantiate
            lifetime: Service lifetime
            **constructor_args: Default constructor arguments
        """
        def factory():
            return cls(**constructor_args)
        
        self.register(service_name, factory, lifetime)
    
    def resolve(self, service_name: str) -> Any:
        """
        Resolve and return a service instance.
        
        Args:
            service_name: Name of service to resolve
            
        Returns:
            Service instance
            
        Raises:
            ServiceNotFoundError: If service not registered
            CircularDependencyError: If circular dependency detected
        """
        # Check for circular dependencies
        if service_name in self._resolution_stack:
            raise CircularDependencyError(
                f"Circular dependency detected: {service_name} "
                f"in resolution stack {self._resolution_stack}"
            )
        
        # Check if service exists
        if service_name not in self._services:
            raise ServiceNotFoundError(f"Service not registered: {service_name}")
        
        service_info = self._services[service_name]
        lifetime = service_info['lifetime']
        
        # Return cached singleton
        if lifetime == self.SINGLETON and service_name in self._singletons:
            return self._singletons[service_name]
        
        # Resolve dependencies
        self._resolution_stack.add(service_name)
        try:
            # Resolve all dependencies first
            resolved_deps = {}
            for dep_name in service_info['dependencies']:
                resolved_deps[dep_name] = self.resolve(dep_name)
            
            # Create instance
            factory = service_info['factory']
            if resolved_deps:
                instance = factory(**resolved_deps)
            else:
                instance = factory()
            
            # Cache if singleton
            if lifetime == self.SINGLETON:
                self._singletons[service_name] = instance
            
            logger.debug(f"Resolved service: {service_name}")
            return instance
            
        finally:
            self._resolution_stack.discard(service_name)
    
    def resolve_all_of(self, service_prefix: str) -> Dict[str, Any]:
        """
        Resolve all services matching a prefix.
        Useful for plugin-like registration patterns.
        
        Example: resolve_all_of('tool_') returns all services starting with 'tool_'
        """
        matching = {}
        for service_name in self._services:
            if service_name.startswith(service_prefix):
                matching[service_name] = self.resolve(service_name)
        return matching
    
    def clear(self) -> None:
        """Clear all services and singletons."""
        self._services.clear()
        self._singletons.clear()
        logger.debug("Service container cleared")
    
    def get_registered_services(self) -> list:
        """Get list of all registered service names."""
        return list(self._services.keys())


# Global container instance
_global_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """Get the global service container."""
    return _global_container


def inject(container: Optional[ServiceContainer] = None) -> Callable:
    """
    Decorator for dependency injection via constructor.
    
    Usage:
        @inject()
        class MyService:
            def __init__(self, logger, config):
                self.logger = logger
                self.config = config
    
    Args:
        container: ServiceContainer to use (default: global)
        
    Returns:
        Decorated class
    """
    def decorator(cls: Type) -> Type:
        original_init = cls.__init__
        
        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            container_to_use = container or get_container()
            
            # Get function signature
            import inspect
            sig = inspect.signature(original_init)
            params = list(sig.parameters.keys())[1:]  # Skip 'self'
            
            # Resolve missing parameters from container
            for param_name in params:
                if param_name not in kwargs and not args:
                    try:
                        kwargs[param_name] = container_to_use.resolve(param_name)
                    except ServiceNotFoundError:
                        # Parameter not in container, will use default or fail
                        pass
            
            original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        return cls
    
    return decorator


def get_service(name: str, container: Optional[ServiceContainer] = None) -> Any:
    """
    Convenience function to get a service from container.
    
    Usage:
        logger = get_service('logger')
    """
    container_to_use = container or get_container()
    return container_to_use.resolve(name)


# Pre-configured WiFi-Tool container setup
def setup_wifi_tool_container() -> ServiceContainer:
    """
    Set up the global DI container with WiFi-Tool services.
    
    Returns:
        Configured ServiceContainer
    """
    container = get_container()
    
    # Register logging services
    from main.utils import (
        wifi_logger,
        attack_logger,
        network_logger,
        security_logger,
        setup_logger
    )
    
    container.register_instance('wifi_logger', wifi_logger)
    container.register_instance('attack_logger', attack_logger)
    container.register_instance('network_logger', network_logger)
    container.register_instance('security_logger', security_logger)
    container.register_instance('setup_logger', setup_logger)
    
    # Register validation services
    from main.utils import (
        validate_essid,
        validate_password,
        validate_ip_address,
        validate_interface_name,
        ValidationError
    )
    
    container.register_instance('validate_essid', validate_essid)
    container.register_instance('validate_password', validate_password)
    container.register_instance('validate_ip_address', validate_ip_address)
    container.register_instance('validate_interface_name', validate_interface_name)
    container.register_instance('ValidationError', ValidationError)
    
    # Register subprocess services
    from main.utils import (
        safe_execute,
        safe_execute_with_output,
        safe_popen
    )
    
    container.register_instance('safe_execute', safe_execute)
    container.register_instance('safe_execute_with_output', safe_execute_with_output)
    container.register_instance('safe_popen', safe_popen)
    
    logger.info("WiFi-Tool DI container configured")
    return container


# Example service factories (can be extended)
class SubprocessExecutor:
    """Encapsulates subprocess execution with DI."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def execute(self, command, sudo=False, quiet=False):
        """Execute command safely."""
        from main.utils import safe_execute
        return safe_execute(command, sudo=sudo, quiet=quiet)
    
    def execute_with_output(self, command, sudo=False):
        """Execute and capture output."""
        from main.utils import safe_execute_with_output
        return safe_execute_with_output(command, sudo=sudo)


class InputValidator:
    """Encapsulates all input validation."""
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_essid(self, essid):
        from main.utils import validate_essid
        return validate_essid(essid)
    
    def validate_password(self, password):
        from main.utils import validate_password
        return validate_password(password)
    
    def validate_ip(self, ip):
        from main.utils import validate_ip_address
        return validate_ip_address(ip)


# Register core services
def register_core_services():
    """Register core infrastructure services."""
    container = get_container()
    
    container.register_class(
        'subprocess_executor',
        SubprocessExecutor,
        lifetime=ServiceContainer.SINGLETON,
        logger=get_service('wifi_logger')
    )
    
    container.register_class(
        'input_validator',
        InputValidator,
        lifetime=ServiceContainer.SINGLETON,
        logger=get_service('wifi_logger')
    )


if __name__ == '__main__':
    # Example usage
    from main.utils import wifi_logger
    
    # Setup container
    setup_wifi_tool_container()
    
    # Register services
    register_core_services()
    
    # Resolve services
    logger = get_service('wifi_logger')
    validator = get_service('input_validator')
    executor = get_service('subprocess_executor')
    
    logger.info("Dependency injection initialized successfully")
    
    # List all registered services
    print("\nRegistered services:")
    for service in get_container().get_registered_services():
        print(f"  -  {service}")
