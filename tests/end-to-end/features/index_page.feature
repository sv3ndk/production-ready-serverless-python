Feature Main page navigation

  Scenario: Main page displays the correct logo
    Given A unauthenticated user
    When They visit the main page
    Then They see the big mouth logo

  Scenario: Main page displays the top restaurants
    Given A unauthenticated user
    When They visit the main page
    Then They see 8 restaurants
