Feature GET restaurants API endpoint

  Scenario: Fetching all restaurants
    Given I call the restaurant API endpoint
    Then I get a list of 8 restaurants
