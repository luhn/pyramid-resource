import pytest
from pyramid_resource import Resource


def test_default_lookup():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        __children__ = {
            'sub': SubResource,
        }

    root = MyResource('request')
    sub = root['sub']
    assert isinstance(sub, SubResource)
    assert sub.request == 'request'
    assert sub.__name__ == 'sub'
    assert sub.__parent__ is root

    with pytest.raises(KeyError):
        root['sub2']


def test_custom_lookup_subclass():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == 'sub'
            return SubResource

    root = MyResource('request')
    sub = root['sub']
    assert isinstance(sub, SubResource)
    assert sub.request == 'request'
    assert sub.__name__ == 'sub'
    assert sub.__parent__ is root


def test_custom_lookup_tuple():
    class SubResource(Resource):
        pass

    class MyResource(Resource):
        def get_child(self, key):
            assert key == 'sub'
            return SubResource, {'foo': 'bar'}

    root = MyResource('request')
    sub = root['sub']
    assert isinstance(sub, SubResource)
    assert sub.request == 'request'
    assert sub.__name__ == 'sub'
    assert sub.__parent__ is root
    assert sub.foo == 'bar'
