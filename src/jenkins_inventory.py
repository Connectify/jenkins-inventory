"""Command line tools to query jenkins."""

import logging
import os

from api4jenkins import Jenkins
from py_dotenv_safe import config

# Configuring logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# dotenv config
options = {
    "dotenvPath": ".env",  # Path to the environment file
    "examplePath": ".env.example",  # Path to the example environment file
    "allowEmptyValues": False,  # Set to True if you want to allow empty values
}


class JenkinsInventory:
    """Interface for querying Jenkins"""

    @classmethod
    def grep(cls):
        # Load environment variables
        config(options)

        # Retrieve configurations from .env
        jenkins_url = os.getenv("JENKINS_URL")
        username = os.getenv("JENKINS_USER")
        password = os.getenv("JENKINS_TOKEN")
        docker_image = os.getenv("DOCKER_IMAGE")

        # Connect to Jenkins
        jenkins = Jenkins(jenkins_url, auth=(username, password))

        # Search for Docker image in each job's configuration
        jobs_using_docker = []

        for item in jenkins.iter():
            try:
                config_xml = item.configure()
                if docker_image and docker_image in config_xml:
                    jobs_using_docker.append(item.url)
            except Exception as e:
                logging.warn(f"Error accessing configuration for {item.url}: {str(e)}")

        # Output results
        for job_url in jobs_using_docker:
            print(f'Docker image "{docker_image}" is used in job at: {job_url}')
