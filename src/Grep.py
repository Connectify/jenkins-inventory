"""Implementation of Jenkins Grep."""

import logging
from argparse import Namespace

from api4jenkins import Jenkins, job

from JobUtils import JobUtils


class Grep:
    """Checking all jobs for a string."""

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
        if args.write:
            JobUtils.write_config(item, args)

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
        pattern = JobUtils.create_pattern(search, args)

        # Search for Docker image in each job's configuration
        for item in jenkins.iter():
            try:
                if JobUtils.is_disabled(item, args):
                    logging.debug(f"Not checking {item.url}: disabled")
                    continue
                if JobUtils.matches(pattern, item.configure()):
                    cls.show_hit(item, pattern, args)
            except Exception as e:
                logging.exception(f"Error accessing configuration for {item.url}: {str(e)}")
