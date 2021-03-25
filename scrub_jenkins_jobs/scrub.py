"""Scrub module"""

import datetime
import functools
import logging
import time
import warnings

import click
import jenkins


def silence_warnings(func):
    """Decorator to silence warning messages."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            return func(*args, **kwargs)

    return wrapper


class ScrubJobs:
    """A class handling everything related to scrubbing jenkins jobs"""

    def __init__(self, url, username, password, ssl_verify=True, dry_run=True):
        """Constructor.

        When a object is instantiated from the class, a connection to the jenkins
        server will be established.

        :param str url: jenkins url
        :param str username: jenkins username for login
        :param str password: jenkins password for login
        :param bool ssl_verify: toggles ssl verification on/off
        :param bool dry_run: toggles dry run mode on/off
        """
        self.connection = jenkins.Jenkins(url, username, password)
        self.connection._session.verify = ssl_verify
        self.todays_date = datetime.date.fromtimestamp(time.time())
        self.dry_run = dry_run

        self.jobs = []
        self.max_days = 30

    @silence_warnings
    def calculate_days_since_last_job_build(self):
        """Calculates the number of days since a jobs last build.

        Default behavior will get all jobs from jenkins and determine
        the number of days since their last build.
        """
        all_jobs = self.connection.get_jobs()
        for job in all_jobs:
            job_name = job['name']
            job_info = self.connection.get_job_info(job_name)

            # Ignore jobs that have not been built yet
            try:
                last_build_number = job_info['lastBuild']['number']
            except TypeError:
                continue

            last_build_info = self.connection.get_build_info(
                job_name, last_build_number)

            last_build_date = datetime.datetime.fromtimestamp(
                last_build_info['timestamp'] / 1000)

            last_build_date = datetime.date(
                last_build_date.year,
                last_build_date.month,
                last_build_date.day
            )

            # Calculate days since last build
            days_since_last_build = abs(last_build_date - self.todays_date).days

            self.jobs.append({
                "name": job_name,
                "lastBuildNumber": last_build_number,
                "lastBuildDate": last_build_date,
                "daysSinceLastBuild": days_since_last_build
            })

    @silence_warnings
    def delete_jobs(self):
        """Deletes jenkins jobs that exceed the maximum number of days."""
        for job in self.jobs:
            job_name = job['name']
            days_since_last_build = job['daysSinceLastBuild']

            if days_since_last_build > self.max_days:
                print(f"Job: {job_name} has not been built in "
                      f"{days_since_last_build}. Deleting job..")
                if not self.dry_run:
                    # self.connection.delete_job(job_name)
                    print(f"Job: {job_name} deleted!")

    def scrub(self):
        """Scrubs the jenkins server for jobs to be purged."""
        self.calculate_days_since_last_job_build()
        self.delete_jobs()


@click.command()
@click.argument("jenkins-url", nargs=1)
@click.argument("jenkins-username", nargs=1)
@click.argument("jenkins-password", nargs=1)
@click.option(
    "--ssl-verify",
    default=False,
    help="Disable SSL verification",
    required=False,
    is_flag=True
)
@click.option(
    "--dry-run",
    default=False,
    help="Simulates the actions that would be taken",
    required=False,
    is_flag=True
)
def cli(jenkins_url, jenkins_username, jenkins_password, ssl_verify, dry_run):
    """Scrub Jenkins Jobs"""
    scrub_jobs = ScrubJobs(
        jenkins_url,
        jenkins_username,
        jenkins_password,
        ssl_verify=ssl_verify,
        dry_run=dry_run
    )

    if dry_run:
        print("-- (Simulation Mode) --")

    scrub_jobs.scrub()
