"""
test_fact.py - Tests for Fact class

test suite for Fact object class

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
import pytest
import datetime
from datetime import timezone

pytestmark = pytest.mark.fact_class


@pytest.mark.parametrize("strings", ["Shatt", "Ion4", "290ugs03", "ThISsTRiNG is AwFuL"])
def test_fact_name(strings, test_fact_empty_fx):
    """
    Test Fact.name getter/setter
    """
    test_fact = test_fact_empty_fx

    test_fact.name = strings
    assert test_fact_empty_fx.name == strings


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_name_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.name = garbage


@pytest.mark.parametrize("strings", ["Shatt", "Ion4", "290ugs03", "ThISsTRiNG is AwFuL"])
def test_fact_lang(strings, test_fact_empty_fx):
    """
    Test Fact.lang getter/setter
    """
    test_fact = test_fact_empty_fx

    test_fact.lang = strings
    assert test_fact_empty_fx.lang == strings


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_lang_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.lang = garbage


@pytest.mark.parametrize("strings", ["Shatt", "Ion4", "290ugs03", "ThISsTRiNG is AwFuL"])
def test_fact_message(strings, test_fact_empty_fx):
    """
    Test Fact.message getter/setter
    """
    test_fact = test_fact_empty_fx

    test_fact.message = strings
    assert test_fact_empty_fx.message == strings


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_message_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.message = garbage


@pytest.mark.parametrize("lists", [['testfact', 'anothertestfact'], ['sometest', 'nowai']])
def test_fact_aliases(lists, test_fact_empty_fx):
    """
    Test Fact.aliases getter/setter
    """
    test_fact = test_fact_empty_fx

    test_fact.aliases = lists
    assert test_fact_empty_fx.aliases == lists


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_alias_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.aliases = garbage


@pytest.mark.parametrize("strings", ["Shatt", "Ion4", "290ugs03", "ThISsTRiNG is AwFuL"])
def test_fact_author(strings, test_fact_empty_fx):
    """
    Test Fact.author getter/setter
    """
    test_fact = test_fact_empty_fx

    test_fact.author = strings
    assert test_fact_empty_fx.author == strings


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_author_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.author = garbage


@pytest.mark.parametrize("strings", ["Shatt", "Ion4", "290ugs03", "ThISsTRiNG is AwFuL"])
def test_fact_editedby(strings, test_fact_empty_fx):
    """
    Test Fact.edited getter/setter
    """
    test_fact = test_fact_empty_fx

    test_fact.editedby = strings
    assert test_fact_empty_fx.editedby == strings


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_editedby_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.editedby = garbage


def test_mfd_flag(test_fact_empty_fx):
    """
    Test Fact.mfd getter/setter
    """
    test_fact = test_fact_empty_fx

    test_fact.mfd = True
    assert test_fact_empty_fx.mfd


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_mfd_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.mfd = garbage


def test_fact_complete(test_fact_fx):
    """
    Test that the fact complete returns properly.
    """
    test_fact = test_fact_fx
    assert test_fact.complete

    # unset
    test_fact.message = ""
    assert not test_fact.complete


def test_fact_edited(test_fact_empty_fx):
    """
    Test that edited generates a datetime automagically, and returns it.
    """
    test_fact = test_fact_empty_fx
    test_fact.edited = datetime.datetime.now(tz=timezone.utc)

    assert test_fact.edited


@pytest.mark.parametrize("garbage", [-1, 4.2, None, ()])
def test_fact_edited_setter(garbage, test_fact_empty_fx):
    """
    Assert that a TypeError is thrown, if the wrong type is passed to the property.
    """
    test_fact = test_fact_empty_fx

    with pytest.raises(TypeError):
        test_fact.edited = garbage

