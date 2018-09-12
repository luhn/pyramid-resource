from pyramid.location import lineage


class Resource:
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
        self._extra = kwargs

    def __getitem__(self, key):
        # Invoke customer child lookup
        resp = self.get_child(key)
        if resp is not None:
            if isinstance(resp, tuple):
                Child, extra = resp
            elif isinstance(resp, Resource):
                Child = resp
                extra = dict()
            else:
                raise TypeError('Invalid child type')
            return Child(self.request, key, self, **extra)

        # Default child lookup
        Child = self.__children__.get(key)
        if Child is not None:
            return Child(self.request, key, self)

        # Couldn't find anything
        raise KeyError

    def get_child(self, key):
        """
        Override this function to dynamically generate child resources.  You
        can return:

        * A Resource subclass
        * A two-tuple of a Resource subclass and a dictionary of extra
            attributes.
        * ``None``, to fall back to default child lookup.

        You can also raise a KeyError to force the tree lookup to stop.

        """
        pass

    def __getattr__(self, name):
        for resource in lineage(self):
            if name in resource._extra:
                return resource._extra[name]
        raise AttributeError('Could not find attribute "{}"'.format(name))
