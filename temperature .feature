Feature: Temperature conversion
  As a user of the converter
  I want to convert temperatures between Celsius, Fahrenheit and Kelvin
  So that I can compare values given on different scales

  Scenario Outline: Freezing and boiling point of water from Celsius
    Given the temperature is <celsius> degrees Celsius
    When I convert it to Fahrenheit
    Then the result is <fahrenheit>

    Examples:
      | celsius | fahrenheit |
      | 0       | 32         |
      | 100     | 212        |
      | -40     | -40        |

  Scenario Outline: Fahrenheit to Celsius
    Given the temperature is <fahrenheit> degrees Fahrenheit
    When I convert it to Celsius
    Then the result is <celsius>

    Examples:
      | fahrenheit | celsius |
      | 32         | 0       |
      | 212        | 100     |

  Scenario Outline: Celsius to Kelvin for water points
    Given the temperature is <celsius> degrees Celsius
    When I convert it to Kelvin
    Then the result is <kelvin>

    Examples:
      | celsius | kelvin |
      | 0       | 273.15 |
      | 100     | 373.15 |

  Scenario: Absolute zero is the lowest allowed temperature
    Given the temperature is -273.15 degrees Celsius
    When I convert it to Kelvin
    Then the result is 0

  Scenario: Temperature below absolute zero is rejected
    Given the temperature is -300 degrees Celsius
    When I try to convert it to Kelvin
    Then the conversion fails with error "temperature below absolute zero"
