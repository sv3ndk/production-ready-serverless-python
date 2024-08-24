from prsl_fixtures import foo
from pytest_bdd import scenario, given, when, then, scenarios

scenarios("../features/index_page.feature")

@given("I am on the main page", target_fixture="index_content")
def get_index_page(foo):
    return foo

@then("I should see the big mouth logo")
def check_big_mouth_logo(index_content):
    assert index_content == "bar"
    pass
