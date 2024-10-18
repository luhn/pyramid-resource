import pytest

from pyramid_resource import Resource


def test_init():
    class MyResource(Resource): ...

    r = MyResource("request", "name", "parent")
    assert r.request == "request"
    assert r.__name__ == "name"
    assert r.__parent__ == "parent"


def test_init_root():
    class MyResource(Resource): ...

    r = MyResource("request")
    assert r.request == "request"
    assert r.__name__ == ""
    assert r.__parent__ is None


def test_init_direct():
    with pytest.raises(TypeError) as e:
        Resource("request")
    assert str(e.value) == (
        "Cannot instanciate `Resource` directly; please make a subclass."
    )


def test_attach():
    class MyResource(Resource): ...

    r = MyResource()
    assert not r.attached
    r.attach("request", "name", "parent")
    assert r.attached
    assert r.request == "request"
    assert r.__name__ == "name"
    assert r.__parent__ == "parent"


def test_default_lookup():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        __children__ = {
            "sub": SubResource,
        }

    root = MyResource("request")
    sub = root["sub"]
    assert isinstance(sub, SubResource)
    assert sub.request == "request"
    assert sub.__name__ == "sub"
    assert sub.__parent__ is root

    with pytest.raises(KeyError):
        root["sub2"]


def test_custom_lookup_subclass():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == "sub"
            return SubResource

    root = MyResource("request")
    sub = root["sub"]
    assert isinstance(sub, SubResource)
    assert sub.request == "request"
    assert sub.__name__ == "sub"
    assert sub.__parent__ is root


def test_custom_lookup_tuple():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == "sub"
            return SubResource, {"foo": "bar"}

    root = MyResource("request")
    sub = root["sub"]
    assert isinstance(sub, SubResource)
    assert sub.request == "request"
    assert sub.__name__ == "sub"
    assert sub.__parent__ is root
    assert sub.foo == "bar"


def test_custom_lookup_instance():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == "sub"
            return SubResource(foo="bar")

    root = MyResource("request")
    sub = root["sub"]
    assert isinstance(sub, SubResource)
    assert sub.request == "request"
    assert sub.__name__ == "sub"
    assert sub.__parent__ is root
    assert sub.foo == "bar"


def test_custom_lookup_none():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == "sub"
            return None

    root = MyResource("request")
    with pytest.raises(KeyError):
        root["sub"]


def test_custom_lookup_unknown():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == "sub"
            return "foo"

    root = MyResource("request")
    with pytest.raises(ValueError) as e:
        root["sub"]
    assert str(e.value) == "Unexpected return value from `get_child`: 'foo'"


def test_getattr():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        subfoo = "subbar"
        _foo = "_bar"

        @property
        def prop(self):
            return "myprop"

    parent = MyResource("request")
    child = SubResource("request", "sub", parent, foo="bar")
    grandchild = SubResource("request", "sub", child)
    assert parent.subfoo == "subbar"
    assert parent.prop == "myprop"
    with pytest.raises(AttributeError) as exc:
        assert parent.foo
    assert str(exc.value) == "'MyResource' object has no attribute 'foo'"
    assert parent._foo == "_bar"

    assert child.foo == "bar"
    assert child.subfoo == "subbar"
    assert child.prop == "myprop"
    # Don't proxy private attributes
    with pytest.raises(AttributeError) as exc:
        assert child._foo
    assert str(exc.value) == (
        "'SubResource' object has no attribute '_foo'.  Note: Resource "
        "objects do not proxy attributes prefixed with an underscore (i.e. "
        "private attributes)."
    )

    assert grandchild.foo == "bar"
    assert grandchild.subfoo == "subbar"
    assert grandchild.prop == "myprop"
