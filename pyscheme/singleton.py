class Singleton(type):
    """Singleton type

    Singletons are fine as long as you don't keep state in them
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FlyWeight(type):
    """FlyWeight type

    The first argument to the constructor must be the identifier of the flyweight
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = args[0]
        if cls not in cls._instances:
            cls._instances[cls] = {}
        if name not in cls._instances[cls]:
            cls._instances[cls][name] = super(FlyWeight, cls).__call__(*args, **kwargs)
        return cls._instances[cls][name]