"""Implementation of Jenkins Grep."""

import logging
import re
from argparse import Namespace

from api4jenkins import Jenkins, job

from Job import ji_job


class Grep:
    """Checking all jobs for a string."""

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

    @classmethod
    def show_matching_line(cls, item: job, line: str) -> None:
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
    def grep(cls, jenkins: Jenkins, search: str, args: Namespace) -> None:
        """
        Implementation of ji_grep.

        Parameters
        ----------
        jenkins : Jenkins
            Connection to Jenkins.
        search : str
            What to look for.
        args : Namespace
            Any other argumentss.
        """
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
                        ji_job.write_config(item)
            except Exception as e:
                logging.exception(f"Error accessing configuration for {item.url}: {str(e)}")
