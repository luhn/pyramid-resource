from importlib import import_module

from pyramid.path import DottedNameResolver


class Resource:
    """
    A node on the traversal resource tree.  Each node should subclass this
    class.  Chilldren can be defined by overriding ``__children__``.

    """

    request = None
    __name__ = ""
    __parent__ = None
    __children__ = dict()
    _children_resolved = False

    def __init__(self, request, name="", parent=None, **kwargs):
        self.request = request
        self.__name__ = name
        self.__parent__ = parent
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not self._children_resolved:
            self.__class__._resolve_children()

    @classmethod
    def _resolve_children(cls):
        assert not cls._children_resolved
        assert cls != Resource

        module = import_module(cls.__module__)
        resolver = DottedNameResolver(module)

        to_update = dict()
        for key, val in cls.__children__.items():
            if isinstance(val, str):
                try:
                    to_update[key] = getattr(module, val)
                except AttributeError:
                    to_update[key] = resolver.resolve(val)
        cls.__children__.update(to_update)
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
