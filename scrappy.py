import sys
import argparse
import logging
from typing import List

from evaluator import evaluate_node, evaluate_program
from exceptions import ScrapError
from lexer import InvalidTokenException, Token, extract_tokens
from parser import Parser
from scrapscript_ast import Program

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format='%(levelname)s: %(message)s'
)


def run_interpreter(source_code: str):
    """
    Takes raw source code as a string and runs it through the
    lexer, parser, and (eventually) evaluator.
    """
    logging.debug("--- Running Lexer ---")
    try:
        tokens: List[Token] = extract_tokens(source_code.splitlines())
        logging.debug(f"Tokens: {tokens}")
    except InvalidTokenException as e:
        logging.error("Lexer failed: Invalid token found.")
        logging.error(e)
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred during lexing: {e}")
        sys.exit(1)

    logging.debug("--- Running Parser ---")
    try:
        parser = Parser(tokens)
        ast: Program = parser.parse_program()
        logging.debug(f"AST: {ast}")
    except Exception as e:
        logging.error(f"Parser failed: {e}")
        sys.exit(1)

    logging.debug("--- Running Evaluator ---")
    try:
        result = evaluate_program(ast)
        print("\n--- Result ---")
        print(result)
    except ScrapError as e:
        logging.error(f"Runtime Error: {e}")
        sys.exit(1)


def main():
    """The main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Scrappy: A ScrapScript Interpreter"
    )

    parser.add_argument(
        "file",
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="The .scrap file to evaluate. If omitted, reads from standard input."
    )

    args = parser.parse_args()

    logging.debug("Reading source code...")
    try:
        source_code = args.file.read()
    finally:
        if args.file is not sys.stdin:
            args.file.close()

    run_interpreter(source_code)


if __name__ == '__main__':
    main()
