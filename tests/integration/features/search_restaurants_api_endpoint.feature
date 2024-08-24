Feature search restaurants API endpoint

  Scenario: Searching themed restaurants
    Given The search_restaurant handler
    When I search for the restaurant with theme $cartoon
    Then I get a list of $4 restaurants
    And All restaurants have the theme $cartoon
