import pytest

from pyramid_resource import Resource


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


def test_getattr():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        subfoo = "subbar"

        @property
        def prop(self):
            return "myprop"

    parent = MyResource("request")
    child = SubResource("request", "sub", parent, foo="bar")
    grandchild = SubResource("request", "sub", child)
    with pytest.raises(AttributeError):
        assert parent.foo
    assert parent.subfoo == "subbar"
    assert parent.prop == "myprop"
    assert child.foo == "bar"
    assert child.subfoo == "subbar"
    assert child.prop == "myprop"
    assert grandchild.foo == "bar"
    assert grandchild.subfoo == "subbar"
    assert grandchild.prop == "myprop"
