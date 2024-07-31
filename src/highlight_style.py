"""Styling for highlights."""

from pygments.style import Style
from pygments.token import Generic, Token

# Create a custom token for search matches
Token.SearchMatch = Generic.Inserted


class SearchHighlightStyle(Style):
    """Simple styling for matches."""

    styles = {
        Token.SearchMatch: "bg:#ff0000 #ffffff",  # red background with white text
    }
