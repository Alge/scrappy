from scrapscript_ast import Identifier


class ScrapError(Exception):
    pass


class ScrapNameError(ScrapError):

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Name '{self.name}' is not defined"


class ScrapTypeError(ScrapError):
    pass


class ScrapEvalError(ScrapError):
    pass


class ScrapParseError(ScrapError):
    pass
