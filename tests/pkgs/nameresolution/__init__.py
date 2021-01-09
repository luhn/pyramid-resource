from pyramid_resource import Resource


class Parent(Resource):
    __children__ = {
        "child": "Child",
    }


class Child(Resource):
    pass
