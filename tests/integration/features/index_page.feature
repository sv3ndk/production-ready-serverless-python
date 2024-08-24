Feature Main page navigation

  Scenario: Main page displays the correct logo
    Given The get_index lambda
    When I navigate to the main page
    Then I see the big mouth logo

  Scenario: Main page displays the top restaurants
    Given The get_index lambda
    When I navigate to the main page
    Then I see 8 restaurants
