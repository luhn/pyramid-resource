from pyramid_resource import Resource


class Parent(Resource):
    __children__ = {
        "child": ".childmodule.Child",
    }
