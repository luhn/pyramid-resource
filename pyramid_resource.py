import venusian


class ResourceMeta(type):
    """
    Metaclass for Resource objects.  This will check if the class requires
    resolution and if so mark it as such.

    """

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
    """
    Return true if a Resource class has children defined with dotted name
    strings.

    """
    for value in cls.__children__.values():
        if isinstance(value, str):
            return True
    return False


class Resource(metaclass=ResourceMeta):
    """
    A node on the traversal resource tree.  This is not meant to be used
    directly but instead subclassed to define new nodes.  Subclasses can
    declare their children by overriding :prop:`__children__` and/or
    dynamically load children by overriding :prop:`.

    If a resource is instanciated without a request, it's considered
    "unattached."  It will need to be attached to a request with :meth:`attach`
    before it can be used in a resource tree.

    Additional keyword arguments will be set as attributes on the object.
    Resource objects will proxy the attributes of its parent and ancestors.

    :param request:  The current Pyramid request, or ``None`` to create an
        "unattached" request.
    :type request:  :class:`pyramid.request.Request` or ``None``
    :param name:  The name of the resource node.
    :type name:  ``str``
    :param parent:  The parent node.
    :type parent:  :class:`Resource`
    :param kwargs:  Additional attributes to set on the class.

    """

    request = None
    __name__ = ""
    __parent__ = None
    __children__ = dict()

    def __init__(self, request=None, name="", parent=None, **kwargs):
        if type(self) is Resource:
            raise TypeError(
                "Cannot instanciate `Resource` directly; please make a "
                "subclass."
            )

        if not self._children_resolved:
            type_name = type(self).__name__
            raise TypeError(
                f"Cannot instanciate resource '{type_name}', "
                "`resolve_children` was never invoked."
            )
        if request is not None:
            self.attach(request, name, parent)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def attach(self, request=None, name="", parent=None):
        """
        Attach a request to a resource.  A resource must be attached to be used
        in a resource tree.

        :raises TypeError:  Resource is already been attached to a request.

        """
        if self.attached:
            raise TypeError(
                "Cannot attach resource, it has already been attached to a "
                "request."
            )
        self.request = request
        self.__name__ = name
        self.__parent__ = parent

    @property
    def attached(self):
        return self.request is not None

    @classmethod
    def resolve_children(cls, config):
        """
        Resolve children with dotted-name strings to the referenced objects.
        If dotted-name strings are being used, this classmethod must be called
        before instantiating.

        """
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
        if not self.attached:
            raise ValueError(
                "Cannot lookup children, resource is not attached to a "
                "request."
            )

        # Default child lookup
        Child = self.__children__.get(key)
        if Child is not None:
            return Child(self.request, key, self)

        # Invoke customer child lookup
        result = self.get_child(key)
        if result is None:
            raise KeyError
        elif isinstance(result, tuple):
            Child, extra = result
            return Child(self.request, key, self, **extra)
        elif isinstance(result, Resource):
            result.attach(self.request, key, self)
            return result
        elif isinstance(result, type) and issubclass(result, Resource):
            return result(self.request, key, self)
        else:
            raise ValueError(
                f"Unexpected return value from `get_child`: {result!r}"
            )

    def get_child(self, key):
        """
        Override this function to dynamically generate child resources.  You
        can return:

        * A Resource subclass.
        * An unattached Resource instance.
        * A two-tuple of a Resource subclass and a dictionary of extra
          attributes.
        * ``None`` or raise an ``AttributeError`` to indicate no child was
          found.

        """
        ...

    def __getattr__(self, name):
        if name.startswith("_"):
            type_name = type(self).__name__
            raise AttributeError(
                f"'{type_name}' object has no attribute '{name}'.  Note: "
                "Resource objects do not proxy attributes prefixed with an "
                "underscore (i.e. private attributes)."
            )

        if self.__parent__ is not None:
            try:
                return getattr(self.__parent__, name)
            except AttributeError:
                # Ignore this AttributeError because we want to throw our own.
                ...

        type_name = type(self).__name__
        raise AttributeError(f"'{type_name}' object has no attribute '{name}'")
