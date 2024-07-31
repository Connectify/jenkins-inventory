"""
Command line tools to query jenkins.

Right now this just provides a way (ji_grep) to search jenkins for a string.

Examples
--------
  poetry run ji_grep example/web-ci
"""

import logging
import os
from argparse import ArgumentParser, Namespace

from api4jenkins import Jenkins
from py_dotenv_safe import config

# dotenv config
options = {
    "dotenvPath": ".env",  # Path to the environment file
    "examplePath": ".env.example",  # Path to the example environment file
    "allowEmptyValues": False,  # Set to True if you want to allow empty values
}


class JenkinsInventory:
    """Interface for querying Jenkins."""

    @classmethod
    def configure_loggers(cls, verbose_level: int) -> None:
        """
        Standard logger config to hid messages from noisy libraries.

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
        parser = ArgumentParser(description="Search for a string in Jenkins jobs")
        parser.add_argument("search", help="The string search for")

        args = cls.std_args(parser)

        cls.grep(args.search)

    @classmethod
    def grep(cls, search: str) -> None:
        """
        Implementation of ji_grep.

        Parameters
        ----------
        search : str
            What to look for.
        """
        # Retrieve configurations from .env
        jenkins_url = os.getenv("JENKINS_URL")
        username = os.getenv("JENKINS_USER")
        password = os.getenv("JENKINS_TOKEN")

        # Connect to Jenkins
        jenkins = Jenkins(jenkins_url, auth=(username, password))

        # Search for Docker image in each job's configuration
        jobs_using_docker = []

        for item in jenkins.iter():
            try:
                config_xml = item.configure()
                if search and search in config_xml:
                    jobs_using_docker.append(item.url)
            except Exception as e:
                logging.exception(
                    f"Error accessing configuration for {item.url}: {str(e)}"
                )

        # Output results
        for job_url in jobs_using_docker:
            logging.info(f'String "{search}" is used in job at: {job_url}')
