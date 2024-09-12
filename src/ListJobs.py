"""Implementation of Jenkins List Jobs."""

import logging
from argparse import Namespace

from api4jenkins import Jenkins

from JobUtils import JobUtils


class ListJobs:
    """Get a list of all jobs."""

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
        pattern = JobUtils.create_pattern(args.match, args) if args.match is not None else None

        # Search for Docker image in each job's configuration
        for item in jenkins.iter():
            try:
                if JobUtils.is_disabled(item, args) or (
                    pattern is not None and not JobUtils.matches(pattern, item.full_name)
                ):
                    continue
                JobUtils.show_job(item)
            except Exception as e:
                logging.exception(f"Error accessing configuration for {item.url}: {str(e)}")
