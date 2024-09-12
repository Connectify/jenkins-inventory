"""Implementation of ji_get_job."""

import logging
from argparse import Namespace

from api4jenkins import Jenkins

from JobUtils import JobUtils


class PutJob:
    """Uploading a job."""

    @classmethod
    def put_job(cls, jenkins: Jenkins, args: Namespace) -> None:
        """
        Implementation of ji_get_job.

        Parameters
        ----------
        jenkins : Jenkins
            Connection to Jenkins.
        args : Namespace
            Any other argumentss.
        """
        # Search for Docker image in each job's configuration
        config = JobUtils.read_xml(jenkins, args)
        job = jenkins.get_job(args.name)
        if job is None:
            jenkins.create_job(args.name, config)
            return
        if job is not None and not args.force:
            logging.fatal(f"Not overwriting job without force: {args.name}")
            return
        job.configure(config)
