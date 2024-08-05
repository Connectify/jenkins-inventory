"""
Command line tools to query jenkins.

Examples
--------
  poetry run ji_grep example/web-ci
"""

import logging
import os
from argparse import ArgumentParser, Namespace

from api4jenkins import Jenkins
from py_dotenv_safe import config

from GetJob import GetJob
from Grep import Grep
from HelpEnvAction import HelpEnvAction
from Job import ji_job
from ListJobs import ListJobs

# dotenv config
options = {
    "dotenvPath": ".env",  # Path to the environment file
    "examplePath": ".env.example",  # Path to the example environment file
    "allowEmptyValues": False,  # Set to True if you want to allow empty values
}


class JenkinsInventory:
    """Interface for querying Jenkins."""

    @classmethod
    def get_connection(cls) -> Jenkins:
        """
        Get the Jenkins connection that the cli will use.

        Returns
        -------
        Jenkins :
            Jenkins connection.
        """
        # Retrieve configurations from .env
        jenkins_url = os.getenv("JENKINS_URL")
        username = os.getenv("JENKINS_USER")
        password = os.getenv("JENKINS_TOKEN")

        # Connect to Jenkins
        return Jenkins(jenkins_url, auth=(username, password))

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
        parser.register("action", "show_help_env", HelpEnvAction)
        parser.add_argument("--help-env", help="Describe .env file.", action="show_help_env")
        parser.add_argument(
            "-v",
            "--verbose",
            help="Show more messages (use -v for DEBUG and requests.INFO, -vv for DEBUG and requests.DEBUG)",
            action="count",
            default=0,
        )
        args = parser.parse_args()

        cls.configure_loggers(args.verbose)
        try:
            # Load environment variables
            config(options)
        except FileNotFoundError:
            logging.warning("No .env found.  Try --help-env for more info.")

        return args

    @classmethod
    def grep_cli(cls) -> None:
        """UI for ji_grep."""
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

        try:
            Grep.grep(cls.get_connection(), args.search, args)
        except KeyboardInterrupt:
            logging.warning("Interrupted")

    @classmethod
    def list_jobs_cli(cls) -> None:
        """UI for ji_list_jobs."""
        parser = ArgumentParser(description="List Jenkins jobs")
        parser.add_argument("-m", "--match", help="The string to look for in the job name.")
        parser.add_argument(
            "-d",
            "--show_disabled",
            help="Show disabled jobs as well.",
            action="store_true",
        )
        parser.add_argument(
            "-i",
            "--ignore_case",
            help="Matches are case insensitive.",
            action="store_true",
        )
        args = cls.std_args(parser)

        try:
            ListJobs.list_jobs(cls.get_connection(), args.search, args)
        except KeyboardInterrupt:
            logging.warning("Interrupted")

    @classmethod
    def get_job_cli(cls) -> None:
        """UI for ji_get_job."""
        parser = ArgumentParser(description="Fetch a Jenkins job")
        parser.add_argument("name", help="The name of the job to get.")
        args = cls.std_args(parser)

        try:
            ji_job.get_job(cls.get_connection(), args.search, args)
        except KeyboardInterrupt:
            logging.warning("Interrupted")

    @classmethod
    def put_job_cli(cls) -> None:
        """UI for ji_put_job."""
        parser = ArgumentParser(description="Upload an XML file fo a given Jenkins job.")
        parser.add_argument("file", help="The XML file to use (read from STDIN if not supplied).")
        parser.add_argument("-n", "--name", help="The name of the job.")
        parser.add_argument(
            "-f", "--force", help="Replace the job if one with this name already exists.", action="store_true"
        )
        args = cls.std_args(parser)

        try:
            GetJob.get_job(cls.get_connection(), args.search, args)
        except KeyboardInterrupt:
            logging.warning("Interrupted")
