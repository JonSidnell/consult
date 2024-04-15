import pytest


@pytest.mark.django_db
def test_nav_links(django_app):
    homepage = django_app.get("/")
    assert len(homepage.html.select(".govuk-header__navigation-item--active")) == 0

    schema_page = homepage.click("Data schema")

    assert len(schema_page.html.select(".govuk-header__navigation-item--active")) == 1
    assert "data schema" in schema_page
