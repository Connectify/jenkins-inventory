"""Implementation of Jenkins List Jobs."""

import logging
from argparse import Namespace

from api4jenkins import Jenkins


class ListJobs:
    """Get a list of all jobs."""

    @classmethod
    def list_jobs(cls, jenkins: Jenkins, search: str, args: Namespace) -> None:
        """
        Implementation of ji_list_jobs.

        Parameters
        ----------
        jenkins : Jenkins
            Connection to Jenkins.
        search : str
            What to look for.
        args : Namespace
            Any other argumentss.
        """
        # Search for Docker image in each job's configuration
        for item in jenkins.iter():
            try:
                if hasattr(item, "disabled") and item.disabled and not args.show_disabled:
                    logging.debug(f"Not checking {item.url}: disabled")
                    continue
            except Exception as e:
                logging.exception(f"Error accessing configuration for {item.url}: {str(e)}")
