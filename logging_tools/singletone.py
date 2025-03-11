import threading

class Singleton(type):
    """
    Метакласс для реализации паттерна Singleton для logger
    """
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Переопределённый метод __call__, который создаёт экземпляр класса,
        если его ещё не существует, или возвращает уже созданный.
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
