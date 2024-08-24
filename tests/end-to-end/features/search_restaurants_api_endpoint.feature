Feature search restaurants API endpoint

  Scenario: Searching themed restaurants
    Given A Cognito authenticated user
    When They search for restaurants with theme $cartoon
    Then They get a list of $4 restaurants
    And All restaurants have the theme $cartoon
