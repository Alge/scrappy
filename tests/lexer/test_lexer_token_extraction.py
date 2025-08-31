
import logging
from lexer import TokenType, extract_tokens

from lexer import Token

import pytest


@pytest.mark.parametrize(
    "test_input, expected_token_types",
    [
        ([""], [TokenType.END_OF_FILE]),

        ([";"], [TokenType.SEMI_COLON, TokenType.END_OF_FILE]),

        # ([" "], [TokenType.WHITE_SPACE, TokenType.END_OF_FILE]),
        # (["\t"], [TokenType.WHITE_SPACE, TokenType.END_OF_FILE]),
        # (["\n"], [TokenType.WHITE_SPACE, TokenType.END_OF_FILE]),
        # ([" \t  \t\n"], [TokenType.WHITE_SPACE, TokenType.END_OF_FILE]),

        (["->"], [TokenType.RIGHT_ARROW, TokenType.END_OF_FILE]),

        ([":"], [TokenType.COLON, TokenType.END_OF_FILE]),

        (["|"], [TokenType.PIPE, TokenType.END_OF_FILE]),

        (["hello"], [TokenType.IDENTIFIER, TokenType.END_OF_FILE]),

        (["+"], [TokenType.PLUS, TokenType.END_OF_FILE]),
        (["++"], [TokenType.DOUBLE_PLUS, TokenType.END_OF_FILE]),

        (["-"], [TokenType.MINUS, TokenType.END_OF_FILE]),

        (["="], [TokenType.EQUALS, TokenType.END_OF_FILE]),

        (["#hello"], [TokenType.ATOM, TokenType.END_OF_FILE]),
        (["#HELLO"], [TokenType.ATOM, TokenType.END_OF_FILE]),
        (["#Hello"], [TokenType.ATOM, TokenType.END_OF_FILE]),
        (["#h"], [TokenType.ATOM, TokenType.END_OF_FILE]),
        (["#H"], [TokenType.ATOM, TokenType.END_OF_FILE]),

        (['"This is some text"'], [TokenType.TEXT, TokenType.END_OF_FILE]),

        (['"hello` "🐸" `frog"'], [TokenType.INTERPOLATED_TEXT, TokenType.END_OF_FILE]),

        (["/"], [TokenType.SLASH, TokenType.END_OF_FILE]),

        (["*"], [TokenType.MULTIPLY, TokenType.END_OF_FILE]),

        ([">>"], [TokenType.PIPE_FORWARD, TokenType.END_OF_FILE]),

        ([">"], [TokenType.GREATER_THAN, TokenType.END_OF_FILE]),

        (["<"], [TokenType.LESS_THAN, TokenType.END_OF_FILE]),

        (["("], [TokenType.START_PARANTHESIS, TokenType.END_OF_FILE]),
        ([")"], [TokenType.END_PARANTHESIS, TokenType.END_OF_FILE]),

        (["1.3"], [TokenType.FLOAT, TokenType.END_OF_FILE]),
        (["3421.3123123123"], [TokenType.FLOAT, TokenType.END_OF_FILE]),
        (["-11.3"], [TokenType.MINUS, TokenType.FLOAT, TokenType.END_OF_FILE]),
        (["-0.0"], [TokenType.MINUS, TokenType.FLOAT, TokenType.END_OF_FILE]),
        (["0.0"], [TokenType.FLOAT, TokenType.END_OF_FILE]),

        (["2"], [TokenType.INTEGER, TokenType.END_OF_FILE]),
        (["2123123"], [TokenType.INTEGER, TokenType.END_OF_FILE]),
        (["0"], [TokenType.INTEGER, TokenType.END_OF_FILE]),
        (["-0"], [TokenType.MINUS, TokenType.INTEGER, TokenType.END_OF_FILE]),
        (["-123123"], [TokenType.MINUS, TokenType.INTEGER, TokenType.END_OF_FILE]),
        (["-5"], [TokenType.MINUS, TokenType.INTEGER, TokenType.END_OF_FILE]),

        (["{"], [TokenType.START_CURLY_BRACKETS, TokenType.END_OF_FILE]),
        (["}"], [TokenType.END_CURLY_BRACKETS, TokenType.END_OF_FILE]),

        (["."], [TokenType.DOT, TokenType.END_OF_FILE]),

        ([","], [TokenType.COMMA, TokenType.END_OF_FILE]),

        (["+<"], [TokenType.APPEND, TokenType.END_OF_FILE]),

        (["~123"], [TokenType.HEXADECIMAL, TokenType.END_OF_FILE]),
        (["~1F3"], [TokenType.HEXADECIMAL, TokenType.END_OF_FILE]),
        (["~abc"], [TokenType.HEXADECIMAL, TokenType.END_OF_FILE]),
        (["~000d"], [TokenType.HEXADECIMAL, TokenType.END_OF_FILE]),

        (["~~aGVsbG8gd29ybGQ="], [TokenType.BASE64, TokenType.END_OF_FILE]),

        (["_"], [TokenType.UNDERSCORE, TokenType.END_OF_FILE]),
        (["!"], [TokenType.EXCLAMATION_MARK, TokenType.END_OF_FILE]),
        (["!HELLO"], [TokenType.EXCLAMATION_MARK,
         TokenType.IDENTIFIER, TokenType.END_OF_FILE]),
        # (["-- This is a comment, and everything here + !? = should be ignored `asd`"],
        #  [TokenType.COMMENT, TokenType.END_OF_FILE]),


    ]
)
def test_token_extraction(test_input, expected_token_types):
    logging.debug(
        f"Trying to find tokens from: {test_input}, expecting {expected_token_types}")

    output = extract_tokens(lines=test_input)

    logging.debug(output)
    for n, token in enumerate(output):
        logging.debug(f"Found token type: {token.token_type}")
        logging.debug(f"expected token: {expected_token_types[n]}")

        assert token.token_type == expected_token_types[n]

    assert len(output) == len(
        expected_token_types), "We should get the right number of tokens back"


@pytest.mark.parametrize(
    "test_input, expected_tokens",
    [
        # Simple, single-token cases
        (";",           [(TokenType.SEMI_COLON, ";")]),
        ("->",          [(TokenType.RIGHT_ARROW, "->")]),
        ("#atomName",   [(TokenType.ATOM, "#atomName")]),
        ("identifier",  [(TokenType.IDENTIFIER, "identifier")]),
        ('"a string"',  [(TokenType.TEXT, '"a string"')]),
        ('"a string with `"expressions"` in it"',
         [(TokenType.INTERPOLATED_TEXT, '"a string with `"expressions"` in it"')]),
        ("123",         [(TokenType.INTEGER, "123")]),
        ("45.67",       [(TokenType.FLOAT, "45.67")]),
        # ("  \t ",      [(TokenType.WHITE_SPACE, "  \t ")]),

        # Multi-token line with different lexemes
        (
            "greet #person ->",
            [
                (TokenType.IDENTIFIER, "greet"),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.ATOM, "#person"),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.RIGHT_ARROW, "->"),
            ]
        ),

        # Test that unary minus is handled correctly as two separate lexemes
        (
            "-52",
            [
                (TokenType.MINUS, "-"),
                (TokenType.INTEGER, "52"),
            ]
        ),

        # A more complex line
        (
            '| #friend n -> "yo" ++ name',
            [
                (TokenType.PIPE, "|"),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.ATOM, "#friend"),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.IDENTIFIER, "n"),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.RIGHT_ARROW, "->"),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.TEXT, '"yo"'),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.DOUBLE_PLUS, "++"),
                # (TokenType.WHITE_SPACE, " "),
                (TokenType.IDENTIFIER, "name"),
            ]
        ),

        # Edge case: Empty input should yield no lexemes
        ("", []),

    ]
)
def test_token_lexemes_are_correct(test_input, expected_tokens):
    """
    This test verifies that the lexer correctly assigns both the
    token type and the exact lexeme string for each token.
    """
    # extract_tokens expects a list of lines
    output_tokens = extract_tokens(lines=[test_input])

    # For easier comparison, we'll create a list of (type, lexeme) tuples
    # from the output, filtering out the final EOF token which has an empty lexeme.
    actual_tokens = [
        (token.token_type, token.lexeme)
        for token in output_tokens
        if token.token_type != TokenType.END_OF_FILE
    ]

    logging.debug(f"Input: '{test_input}'")
    logging.debug(f"Expected: {expected_tokens}")
    logging.debug(f"Actual:   {actual_tokens}")

    # The main assertion: the list of (type, lexeme) tuples should be identical.
    assert actual_tokens == expected_tokens
