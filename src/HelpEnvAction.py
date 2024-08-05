"""Object for handleing special help option."""

import shutil
import textwrap
from argparse import SUPPRESS, Action, ArgumentParser, Namespace
from typing import Any, Optional, Sequence


class HelpEnvAction(Action):
    """
    Implementation.

    Parameters
    ----------
    option_strings : list
        Strings to associate with this action.
    dest : str
        Name of attribute to hold object.
    default : str
        Value if nothing is specifiedd.
    help : Optional[str]
        Description of argument.
    """

    def __init__(
        self,
        option_strings: list[str],
        dest: str = SUPPRESS,
        default: Optional[str] = SUPPRESS,
        help: Optional[str] = "",
    ):
        """
        Create a HelpEnvAction object.

        Parameters
        ----------
        option_strings : list
            Strings to associate with this action.
        dest : str
            Name of attribute to hold object.
        default : str
            Value if nothing is specifiedd.
        help : Optional[str]
            Description of argument.
        """
        super(HelpEnvAction, self).__init__(
            option_strings=option_strings, dest=dest, default=default, nargs=0, help=help
        )

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Optional[str | Sequence[Any]],
        option_string: Optional[str] = None,
    ) -> None:
        """
        A help message explaining the needed entries in .env.

        Parameters
        ----------
        parser : ArgumentParser
            Ye old parser.
        namespace : Namespace
            Attribute holder.
        values : list
            Argument values.
        option_string : str
            String for the option.
        """
        help_message = """Environment Variable Help:
        --------------------------

        The .env file in the current directory should contain the following information for Jenkins:

        - JENKINS_URL: Your Jenkins instance URL.
        - JENKINS_USER: Your Jenkins username.
        - JENKINS_TOKEN: Your Jenkins API token."""

        colwidth = shutil.get_terminal_size().columns
        paragraphs = help_message.strip().split("\n")
        wrapped_paragraphs = [textwrap.fill(textwrap.dedent(paragraph), width=colwidth) for paragraph in paragraphs]
        print("\n".join(wrapped_paragraphs))
        parser.exit()
