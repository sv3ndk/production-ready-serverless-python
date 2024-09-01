Feature ordering meals

  Scenario: Happy path scenario
    Given A Cognito authenticated user
    And A restaurant waiting for orders
    When The user orders a meal at Leaky Cauldron
    Then An order ID is returned
    And The restaurant Leaky Cauldron is notified of the order
