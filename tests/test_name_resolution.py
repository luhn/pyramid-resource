def test_name_resolution():
    from tests.pkgs.nameresolution import Child, Parent

    context = Parent("request")
    assert isinstance(context["child"], Child)


def test_dotted_name_resolution():
    from tests.pkgs.dottednameresolution import Parent
    from tests.pkgs.dottednameresolution.childmodule import Child

    context = Parent("request")
    assert isinstance(context["child"], Child)
