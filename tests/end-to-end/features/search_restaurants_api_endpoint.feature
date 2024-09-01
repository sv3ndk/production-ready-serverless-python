Feature search restaurants API endpoint

  Scenario: Searching themed restaurants
    Given A Cognito authenticated user
    When They search for restaurants with theme cartoon
    Then A list of 4 restaurants is received
    And All restaurants have the theme cartoon
