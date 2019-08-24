import venusian
from pyramid.path import caller_package, DottedNameResolver


class ResourceMeta(type):
    def __new__(cls, name, bases, attrs):
        Class = type.__new__(cls, name, bases, attrs)

        # If any children are strings, mark for resolution.
        if any(isinstance(x, str) for x in Class.__children__.values()):
            package = caller_package()
            venusian.attach(Class, _resolver_factory(package))

        return Class


def _resolver_factory(package):
    _resolver = DottedNameResolver(package)

    def resolve(scanner, name, obj):
        children = obj.__children__
        for name, child in children.items():
            if isinstance(child, str):
                children[name] = _resolver.resolve(child)

    return resolve


class Resource(metaclass=ResourceMeta):
    """
    A node on the traversal resource tree.  Each node should subclass this
    class.  Chilldren can be defined by overriding ``__children__``.

    """
    request = None
    __name__ = ''
    __parent__ = None
    __children__ = dict()

    def __init__(self, request, name='', parent=None, **kwargs):
        self.request = request
        self.__name__ = name
        self.__parent__ = parent
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        # Default child lookup
        Child = self.__children__.get(key)
        if Child is not None:
            return Child(self.request, key, self)

        # Invoke customer child lookup
        resp = self.get_child(key)
        if resp is not None:
            Child, extra = resp if isinstance(resp, tuple) else (resp, dict())
            return Child(self.request, key, self, **extra)

        # Couldn't find anything
        raise KeyError

    def get_child(self, key):
        """
        Override this function to dynamically generate child resources.  You
        can return:

        * A Resource subclass
        * A two-tuple of a Resource subclass and a dictionary of extra
            attributes.
        * ``None`` to indicate no child was found.

        """
        pass

    def __getattr__(self, name):
        if self.__parent__:
            return getattr(self.__parent__, name)
        else:
            raise AttributeError('Could not find attribute "{}"'.format(name))
