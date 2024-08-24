Feature GET restaurants API endpoint

  Scenario: Fetching all restaurants
    Given An IAM authenticated user
    When They call the restaurant API endpoint
    Then They get a list of $8 restaurants
