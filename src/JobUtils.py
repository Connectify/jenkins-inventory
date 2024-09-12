"""Our utilites for Jenkins jobs."""

import logging
import os
import re
import sys
from argparse import Namespace

import defusedxml.ElementTree as ET
from api4jenkins import job


class JobUtils:
    """Jenkins Job utils."""

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
    def is_disabled(cls, job: job, args: Namespace) -> bool:
        """
        Determine if a job is disabled and if we are ignoring disabled jobs.

        Parameters
        ----------
        job : job
            Item to show.
        args : Namespace
            Any arguments.

        Returns
        -------
        bool :
            True if this job should be skipped.
        """
        return hasattr(job, "disabled") and job.disabled and not args.show_disabled

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
    def matches(cls, needle: str, haystack: str) -> bool:
        """
        Return true if needle is in the haystack.

        Parameters
        ----------
        needle : str
            String to look for.
        haystack : str
            String to look in.

        Returns
        -------
        bool :
            Found or not.
        """
        if not isinstance(needle, str) or not isinstance(needle, str):
            return False
        return re.search(needle, haystack) is not None

    @classmethod
    def create_valid_filename(cls, title: str) -> str:
        """
        Remove or replace invalid characters not allowed in file names.

        Parameters
        ----------
        title : str
            The string to alter.

        Returns
        -------
        str :
            A valid file name.
        """
        title = re.sub(r'[<>:"/\\|?*]', "", title)
        title = re.sub(r"\s+", "-", title)
        title = title.strip("-")
        if not title.endswith(".xml"):
            title += ".xml"
        return title

    @classmethod
    def write_config(cls, item: job, args: Namespace) -> None:
        """
        Write the configuration for the job to a file.

        Parameters
        ----------
        item : job
            Jenkins job to write.
        args : Namespace
            Any other arguments.
        """
        name = args.filename if args.filename is not None else item.display_name
        if name is None or name == "":
            logging.warning("Cannot use name for filename. Using url.")
            name = item.url
        name = cls.create_valid_filename(name) if name != "-" else "-"
        if os.path.exists(name) and not args.force and name != "-":
            logging.warning(f"Not overwriting {name}")
            return
        content = item.configure()
        if name == "-":
            sys.stdout.write(content)
            return
        logging.info(f"Saving {item.url} to {name}")
        with open(name, "w") as file:
            file.write(content)

    def read_xml(cls, args: Namespace) -> str:
        """
        Read XML for a job.

        Parameters
        ----------
        args : Namespace
            Any other arguments.

        Returns
        -------
        str :
            The xml.
        """
        if args.file == "-":
            content = sys.stdin.read()
        else:
            with open(args.file) as file:
                content = file.read()

        try:
            ET.fromstring(content)
        except ET.ParseError as e:
            raise ValueError(f"Provided XML could not be validated: {e}")
        return content
