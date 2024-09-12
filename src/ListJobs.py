"""Implementation of Jenkins List Jobs."""

import logging
from argparse import Namespace

from api4jenkins import Jenkins, job


class ListJobs:
    """Get a list of all jobs."""

    @classmethod
    def show_job(cls, job: job) -> None:
        """
        Show a job.

        Parameters
        ----------
        job : job
            Item to show.
        """
        logging.info(job.full_name)

    @classmethod
    def list_jobs(cls, jenkins: Jenkins, args: Namespace) -> None:
        """
        Implementation of ji_list_jobs.

        Parameters
        ----------
        jenkins : Jenkins
            Connection to Jenkins.
        args : Namespace
            Any other argumentss.
        """
        # Search for Docker image in each job's configuration
        for item in jenkins.iter():
            try:
                if hasattr(item, "disabled") and item.disabled and not args.show_disabled:
                    continue
                cls.show_job(item)
            except Exception as e:
                logging.exception(f"Error accessing configuration for {item.url}: {str(e)}")
