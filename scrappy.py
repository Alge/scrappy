
import sys
from typing import Iterable, List
from lexer import InvalidTokenException, extract_tokens
from models import Token

import logging


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


def read_file(file_path: str) -> Iterable[str]:
    return open(file_path, "r").readlines()


def run(file_path: str):

    # First read the file

    logging.debug("Reading .scrap file")
    try:
        raw_code = read_file(file_path=file_path)
    except Exception as e:
        logging.error(f"Failed reading .scrap file: {e}")
        sys.exit(1)

    logging.debug("Running lexer")
    # Do the lexing
    try:
        tokens: List[Token] = extract_tokens(raw_code)
        for token in tokens:
            logging.debug(f"Found token: {token}")
    except InvalidTokenException as e:
        logging.error(f"Failed parsing token.")
        logging.error(f"{e.__repr__()}")

    logging.debug("Running parser")
    # Parse

    logging.debug("Executing code")
    # Execute


def print_help() -> None:
    print("""Usage:

scrappy.py <filename>.scrap
""")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        logging.debug(f"sys.argv: {sys.argv}")
        print_help()
        sys.exit(1)

    file_path = sys.argv[1]

    if not file_path.endswith(".scrap"):
        logging.error(
            "I don't know how to run non-scrap files (file needs to end in .scrap)")
        sys.exit(1)

    run(file_path=file_path)
