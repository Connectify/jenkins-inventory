"""Implementation of ji_get_job."""

import logging
from argparse import Namespace

from api4jenkins import Jenkins

from JobUtils import JobUtils


class GetJob:
    """Checking all jobs for a string."""

    @classmethod
    def get_job(cls, jenkins: Jenkins, name: str, args: Namespace) -> None:
        """
        Implementation of ji_get_job.

        Parameters
        ----------
        jenkins : Jenkins
            Connection to Jenkins.
        name : str
            The job to get.
        args : Namespace
            Any other argumentss.
        """
        job = jenkins.get_job(name)
        if job is not None:
            JobUtils.write_config(job, args)
            return
        logging.fatal(f"No job found for '{name}'")
