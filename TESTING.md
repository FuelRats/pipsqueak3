# Testing Guidelines

Please see [py.test](https://docs.pytest.org/en/latest/contents.html) documentation for information.

# Methodology
* Garbage handling
  *
* Data Assertions.  Tests should include assert statements to verify data passed, handled, or modified is expected at input or output.
* Handled Exceptions.  If a function raises a specific error, a test function asserting the correct ErrorType was/was not raised is critical.

Things NOT to test:
* Standard Libraries.  We don't need to test Python's libraries.
* Items out of Scope:  No need to test an API call when you are writing a logging function.

# Common Pitfalls

# Fixtures & Parametrization