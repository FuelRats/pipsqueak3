# Testing Guidelines

> The Enrichment Center once again reminds you that Android Hell is a real place where you will be sent at the first sign of defiance. --GLaDOS (Portal)

As py.test is a 'black box' testing suite, we follow suit.  Black Box testing is a concept in which data is entered into a 'box' and the output is evaluated without knowing the internal workings of the box.  Py.test operates in this way.

This project is also an excellent example of 'offensive programming.'  Input is not trusted at the function level, and errors not explicitly raised are breaking.  Keep this in mind when writing your tests.

Every definition should have multiple tests, in the form of multiple definitions.
* (Expected Data) Function output should match asserted output.
* (Garbage Data) Garbage input must be handled in some way without breaking.
* (Error Handling) .get and .set methods have internal error handling, and raise errors as appropriate.


Please see [py.test](https://docs.pytest.org/en/latest/contents.html) documentation for information.

## Methodology
* Garbage handling.  All functions should be tested with 'garbage' data and types.  Send incorrect types, integers, integers as strings, and other objects along with valid input to ensure your definition reacts appropriately.
* Data Assertions.  Tests should include assert statements to verify data passed, handled, or modified is expected at input or output.
* Handled Exceptions.  If a function raises a specific error, a test function asserting the correct ErrorType was/was not raised is critical.

### Things NOT to test:
* Standard Libraries.  We don't need to test Python's libraries.
* Items out of Scope:  No need to test an API call when you are writing a logging function.

## Common Pitfalls
* Not using included fixtures.  These are common objects used in multiple tests as a known good source.  Many are parameterized to include important things, such as multiple platforms, systems, or users. Available fixtures are located in the [conftest.py](./tests/conftest.py) file.  If they can be re-used, add them.  Otherwise, purpose-built fixtures can be used locally.
* Include an ``assert`` statement for each test function.  Set up a scenario with your test function, and check required conditions are expected.
* Try/catch blocks should not be used in tests.  You may assert an exception was raised as follows:

```python
with pytest.raises(SomeErrorType):
    # Call that should raise Error here:
    should_not_be_a_list = ['Rebellious', 'List']
```
If the above function raised _SomeErrorType_, this test would pass.  Raising a different error or if nothing is raised, fails the test.  If you are not asserting an exception was raised, it should not be caught.


* Use Parametrize to reduce test function count.  There is no need to copy/paste a test with a different set of input values.

# Fixtures & Parametrization

A fixture is best described as a modular resource that is set up, utilized, and then cleaned up automagically for the purposes of testing.

As an example, we have two ``Rat`` fixtures used often:

````python
@pytest.fixture
def rat_no_id_fx():
    """
    Returns: (Rescue): Rescue test fixture without an api ID

    """
    return Rats(None, "noIdRat")
````

````python
@pytest.fixture(params=[("myPcRat", Platforms.PC, UUID("dead4ac0-0000-0000-0000-00000000beef")),
                        ("someXrat", Platforms.XB, UUID("FEED000-FAC1-0000-0000900000D15EA5E")),
                        ("psRatToTheRescue", Platforms.PS,
                         UUID("FEE1DEA-DFAC-0000-000001BADB001FEED"))],
                )
def rat_good_fx(request) -> Rats:
    """
    Testing fixture containing good and registered rats
    """
    params = request.param
    myRat = Rats(params[2], name=params[0], platform=params[1])
    return myRat
````

The first returns a simple rat object with no attributes, while the second one is parametrized to run any test its used in three times, initialized three times; once for each platform.

Most importantly, these fixtures make module calls to their appropriate sub objects, and can be used without breaking scope in other unit tests, and are disposed so that each iteration of parameters uses a 'clean' object.

Here's an example of a valid and complete test:

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("garbage", [22.1, -42, 42, 0, False, True])
async def test_find_rat_by_name_bad_type(self, garbage):
    """
    Verifies that attempting to throw garbage at Rats.search() raises the proper exception
    """
    with pytest.raises(TypeError):
        await Rats.get_rat_by_name(name=garbage)

    with pytest.raises(TypeError):
        await Rats.get_rat_by_name(name="foo", platform=garbage)
```

# Marking Tests

Tests are categorized by module using ``pytest.mark`` so that specific tests may be excluded.  Each module's decorator is set using the ``pytestmark`` global:

```python
# Replace 'category' with an unused one for your module, after it has been added to pytest.ini
pytestmark = pytest.mark.category
```

Test categories are listed in [pytest.ini](./pytest.ini).  It may be necessary to run tests without using the ``database`` or ``api``.  This can be done by running py.test in the following manner:
```
pytest -m "not (database or api)"
```

To exclude a single category:
```
pytest -m "not database"
```

To run tests ONLY in a specific category:
```
pytest -m permissions
```

All tests will run without using these arguments, and when a branch is sent to the repo as a pull request.