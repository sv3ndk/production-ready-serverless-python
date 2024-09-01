Feature ordering meals

  Scenario: Restaurant receives the order
    Given A Cognito authenticated user
    And A restaurant waiting for orders
    When The user orders a meal at Leaky Cauldron
    Then An order ID is returned synchronously
    And The restaurant Leaky Cauldron is notified of the order

  Scenario: Order is visible in the bus
    Given A Cognito authenticated user
    And A probe on the event bus
    When The user orders a meal at Pizza Planet
    Then An order ID is returned synchronously
    And The event bus probe receives an order event for Pizza Planet
