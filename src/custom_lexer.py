"""The Custom lexer that extends XML."""

from pygments.lexers import XmlLexer
from pygments.token import Token


# Use XmlLexer and provide custom formatting upon encountering our special markup
class XmlCustomLexer(XmlLexer):
    """
    Extending the processor.
    """

    def get_tokens_unprocessed(self, text: str):
        """
        Get unprocessed tokens.

        Parameters
        ----------
        text : str
            Text to be processed.
        """
        for index, token, value in XmlLexer.get_tokens_unprocessed(self, text):
            if "{{search_highlight}}" in value:
                value = value.replace("{{search_highlight}}", "")
                value = value.replace("{{/search_highlight}}", "")
                yield index, Token.SearchMatch, value
            else:
                yield index, token, value
