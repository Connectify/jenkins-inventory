"""
Command line tools to query jenkins.

Right now this just provides a way (ji_grep) to search jenkins for a string.

Examples
--------
  poetry run ji_grep example/web-ci
"""

import logging
import os
import re
from argparse import ArgumentParser, Namespace

from api4jenkins import Jenkins, job
from py_dotenv_safe import config
from pygments import highlight
from pygments.formatters import TerminalFormatter

from custom_lexer import XmlCustomLexer
from highlight_style import SearchHighlightStyle

# dotenv config
options = {
    "dotenvPath": ".env",  # Path to the environment file
    "examplePath": ".env.example",  # Path to the example environment file
    "allowEmptyValues": False,  # Set to True if you want to allow empty values
}


class JenkinsInventory:
    """Interface for querying Jenkins."""

    @classmethod
    def create_valid_filename(cls, title: str) -> str:
        """
        Remove or replace invalid characters not allowed in file names.

        Parameters
        ----------
        title : str
            The string to alter.

        Returns
        -------
        str :
            A valid file name.
        """
        title = re.sub(r'[<>:"/\\|?*]', "", title)
        title = re.sub(r"\s+", "-", title)
        title = title.strip("-")
        return title

    @classmethod
    def configure_loggers(cls, verbose_level: int) -> None:
        """
        Standard logger config to hide messages from noisy libraries.

        Parameters
        ----------
        verbose_level : int
            Level of verbosity.  0 for minimal.
        """
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        loggers_to_configure = [
            "api4jenkins.http",
            "httpx",
            "httpcore.connection",
            "httpcore.http11",
            "httpcore.http2",
            "httpcore.proxy",
            "httpcore.socks",
        ]

        root_level = logging.INFO
        their_level = logging.WARNING
        if verbose_level < 1:
            log_format = "%(message)s"
        if verbose_level >= 1:
            root_level = logging.DEBUG
            their_level = logging.INFO
        if verbose_level >= 2:
            their_level = logging.DEBUG

        # Set logging for specific modules
        for logger_name in loggers_to_configure:
            logging.getLogger(logger_name).setLevel(their_level)

        logging.basicConfig(level=root_level, format=log_format)

    @classmethod
    def std_args(cls, parser: ArgumentParser) -> Namespace:
        """
        Standard arg parsing.

        Parameters
        ----------
        parser : ArgumentParser
            Argument handler to augment with std args.

        Returns
        -------
        Namespace :
            Parsed arguments.
        """
        # Load environment variables
        config(options)

        parser.add_argument(
            "-v",
            "--verbose",
            help="Show more messages (use -v for DEBUG and requests.INFO, -vv for DEBUG and requests.DEBUG)",
            action="count",
            default=0,
        )
        args = parser.parse_args()
        cls.configure_loggers(args.verbose)
        return args

    @classmethod
    def grep_cli(cls) -> None:
        """UI for ji_grep."""
        try:
            parser = ArgumentParser(description="Search for a string in Jenkins jobs")
            parser.add_argument("search", help="The string search for")
            parser.add_argument("-l", "--list", help="Only show the url", action="store_true")
            parser.add_argument(
                "-d",
                "--show_disabled",
                help="Show disabled jobs as well.",
                action="store_true",
            )
            parser.add_argument(
                "-w",
                "--write",
                help="Save matched configuration using the name of the job as the filename.",
                action="store_true",
            )
            parser.add_argument(
                "-i",
                "--ignore_case",
                help="Matches are case insensitive.",
                action="store_true",
            )
            args = cls.std_args(parser)

            cls.grep(args.search, args)
        except KeyboardInterrupt:
            logging.warning("Interrupted")

    @classmethod
    def write_config(cls, item: job) -> None:
        """
        Write the configuration for the job to a file.

        Parameters
        ----------
        item : job
            Jenkins job to write.
        """
        name = item.display_name
        if name is None or name == "":
            logging.warning("Cannot use name for filename. Using url.")
            name = item.url
        name = cls.create_valid_filename(name) + ".xml"
        if os.path.exists(name):
            logging.warning(f"Not overwriting {name}")
            return
        logging.info(f"Saving {item.url} to {name}")
        with open(name, "w") as file:
            file.write(item.configure())

    @classmethod
    def create_pattern(cls, search: str, args: Namespace) -> str:
        """
        Get a pattern to match our string.

        Parameters
        ----------
        search : str
            String to turn into a pattern.
        args : Namespace
            Any other arguments.

        Returns
        -------
        str :
            Pattern to use for matching.
        """
        pattern = re.escape(search)
        if args.ignore_case:
            pattern = "(?i)" + pattern

        return pattern

    @classmethod
    def show_hit(cls, item: job, search: str, args: Namespace) -> None:
        """
        Format any hits for display.

        Parameters
        ----------
        item : job
            Jenkins job that matched.
        search : str
            To be highlighted.
        args : Namespace
            Any other argumentss.
        """
        url = item.url
        if args.list:
            logging.info(url)
            return

        # Highlight terms using a special Token type
        xml = item.configure()
        highlighted_xml = re.sub(
            search,
            lambda m: f"{{{{search_highlight}}}}{m.group(0)}{{{{/search_highlight}}}}",
            xml,
            flags=re.IGNORECASE,
        )

        # Produce highlighted XML using Pygments and custom style
        highlighted_xml = highlight(
            highlighted_xml,
            XmlCustomLexer(),
            TerminalFormatter(style=SearchHighlightStyle),
        )

        for line in highlighted_xml.splitlines():
            if cls.has_hit(search, line, args):
                cls.show_matching_line(item, line)

    @classmethod
    def show_matching_line(cls, item: job, line: str):
        """
        Show the matching line in the job.

        Parameters
        ----------
        item : job
            The job.
        line : str
            The matching line, formatted for display.
        """
        name = item.display_name
        if name is None:
            logging.info(f"{item.url}: {line}")
            return
        logging.info(f"{name} ({item.url}): {line}")

    @classmethod
    def has_hit(cls, needle: str, haystack: str, args: Namespace) -> bool:
        """
        Return true if needle is in the haystack.

        Parameters
        ----------
        needle : str
            String to look for.
        haystack : str
            String to look in.
        args : Namespace
            Any other argumentss.

        Returns
        -------
        bool :
            Found or not.
        """
        if not isinstance(needle, str):
            return False
        return re.search(needle, haystack) is not None

    @classmethod
    def grep(cls, search: str, args: Namespace) -> None:
        """
        Implementation of ji_grep.

        Parameters
        ----------
        search : str
            What to look for.
        args : Namespace
            Any other argumentss.
        """
        # Retrieve configurations from .env
        jenkins_url = os.getenv("JENKINS_URL")
        username = os.getenv("JENKINS_USER")
        password = os.getenv("JENKINS_TOKEN")

        # Connect to Jenkins
        jenkins = Jenkins(jenkins_url, auth=(username, password))

        # Escape the search term to handle special characters safely
        pattern = cls.create_pattern(search, args)

        # Search for Docker image in each job's configuration
        for item in jenkins.iter():
            try:
                if hasattr(item, "disabled") and item.disabled and not args.show_disabled:
                    logging.debug(f"Not checking {item.url}: disabled")
                    continue
                if cls.has_hit(pattern, item.configure(), args):
                    cls.show_hit(item, pattern, args)
                    if args.write:
                        cls.write_config(item)
            except Exception as e:
                logging.exception(f"Error accessing configuration for {item.url}: {str(e)}")
