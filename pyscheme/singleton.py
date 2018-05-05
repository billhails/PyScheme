class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FlyWeight(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        name = args[0]
        if cls not in cls._instances:
            cls._instances[cls] = {}
        if name not in cls._instances[cls].keys():
            cls._instances[cls][name] = super(FlyWeight, cls).__call__(*args, **kwargs)
        return cls._instances[cls][name]