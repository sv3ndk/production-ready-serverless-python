Feature Main page navigation

  Scenario: Main page displays the correct logo
    Given I am on the main page
    Then I see the big mouth logo

  Scenario: Main page displays the top restaurants
    Given I am on the main page
    Then I see 8 restaurants
