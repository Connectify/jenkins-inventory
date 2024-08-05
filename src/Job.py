"""Our utilites for Jenkins jobs."""

import logging
import os
import re

from api4jenkins import job


class ji_job:
    """Jenkins Job utils."""

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
        return title

    @classmethod
    def write_config(cls, item: job) -> None:
        """
        Write the configuration for the job to a file.

        Parameters
        ----------
        item : job
            Jenkins job to write.
        """
        name = item.display_name
        if name is None or name == "":
            logging.warning("Cannot use name for filename. Using url.")
            name = item.url
        name = cls.create_valid_filename(name) + ".xml"
        if os.path.exists(name):
            logging.warning(f"Not overwriting {name}")
            return
        logging.info(f"Saving {item.url} to {name}")
        with open(name, "w") as file:
            file.write(item.configure())
