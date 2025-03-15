import threading

class Singleton(type):
    """
    Metaclass for implementing the Singleton pattern for a logger.
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Overridden __call__ method that creates an instance of the class
        if it does not already exist, or returns the existing one.
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
