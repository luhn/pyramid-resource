import venusian


class ResourceMeta(type):
    def __new__(cls, name, bases, dct):
        obj = super().__new__(cls, name, bases, dct)
        if bases == tuple():
            # Skip everything else for base Resource class.
            return obj

        if _requires_resolution(obj):
            obj._children_resolved = False

            def resolve(scanner, name, config):
                obj.resolve_children(scanner.config)

            venusian.attach(obj, resolve, category="pyramid")
        else:
            obj._children_resolved = True
        return obj


def _requires_resolution(cls):
    for value in cls.__children__.values():
        if isinstance(value, str):
            return True
    return False


class Resource(metaclass=ResourceMeta):
    """
    A node on the traversal resource tree.  Each node should subclass this
    class.  Chilldren can be defined by overriding ``__children__``.

    """

    request = None
    __name__ = ""
    __parent__ = None
    __children__ = dict()

    def __init__(self, request, name="", parent=None, **kwargs):
        if not self._children_resolved:
            raise TypeError(
                "Cannot instanciate resource, `resolve_children` was never "
                "invoked."
            )
        self.request = request
        self.__name__ = name
        self.__parent__ = parent
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def resolve_children(cls, config):
        if cls is Resource:
            raise NotImplementedError(
                "Cannot run `resolve_children` on base `Resource` object."
            )

        # If already resolved, no-op
        if cls._children_resolved:
            return

        # We're using list() to create a copy of the item list, to prevent
        # issues when modifying the dictionary in-place.
        for key, val in list(cls.__children__.items()):
            if isinstance(val, str):
                cls.__children__[key] = config.maybe_dotted(val)
        cls._children_resolved = True

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
