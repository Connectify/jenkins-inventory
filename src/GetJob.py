"""Implementation of ji_get_job."""

import logging
from argparse import Namespace

from api4jenkins import Jenkins

from Job import ji_job


class GetJob:
    """Checking all jobs for a string."""

    @classmethod
    def get_job(cls, jenkins: Jenkins, search: str, args: Namespace) -> None:
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

        # Search for Docker image in each job's configuration
        for item in jenkins.iter():
            try:
                if hasattr(item, "disabled") and item.disabled and not args.show_disabled:
                    logging.debug(f"Not checking {item.url}: disabled")
                    continue
                if args.write:
                    ji_job.write_config(item)
            except Exception as e:
                logging.exception(f"Error accessing configuration for {item.url}: {str(e)}")
