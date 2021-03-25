"""Scrub module"""

import datetime
import functools
import logging
import re
import time
import warnings

import click
import jenkins
import yaml

from scrub_jenkins_jobs import click_callbacks
from scrub_jenkins_jobs import constants


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

    def __init__(self, url, username, password, ssl_verify=constants.SSL_VERIFY,
                 dry_run=constants.DRY_RUN, max_days=constants.MAX_DAYS, regex_ignore_jobs=(),
                 ignore_jobs=(), config_file=constants.CONFIG_FILE, only_jobs=()):
        """Constructor.

        When a object is instantiated from the class, a connection to the jenkins
        server will be established.

        :param str url: jenkins url
        :param str username: jenkins username for login
        :param str password: jenkins password for login
        :param bool ssl_verify: toggles ssl verification on/off
        :param bool dry_run: toggles dry run mode on/off
        :param int max_days: maximum number of days a job can stick around for
        :param tuple regex_ignore_jobs: regular expressions to ignore matching jobs
        :param tuple ignore_jobs: ignore jobs from being matched
        :param tuple only_jobs: exact jobs to scrub (overrides all other filters)
        """
        self.connection = jenkins.Jenkins(url, username, password)
        self.connection._session.verify = ssl_verify
        self.todays_date = datetime.date.fromtimestamp(time.time())
        self.dry_run = dry_run

        self.jobs = []
        self.max_days = max_days
        self.config_file = config_file

        self.regex_ignore_jobs = list(regex_ignore_jobs)
        self.ignore_jobs = list(ignore_jobs)
        self.only_jobs = list(only_jobs)

        self.load_config()

    def load_config(self):
        """Load configuration file."""
        if self.config_file is None:
            return

        with open(self.config_file, "r") as stream:
            config = yaml.load(stream, Loader=yaml.FullLoader)

        for item in config.get('regex_ignore_jobs', []):
            if item not in self.regex_ignore_jobs:
                self.regex_ignore_jobs.append(item)

        for item in config.get('ignore_jobs', []):
            if item not in self.ignore_jobs:
                self.ignore_jobs.append(item)

        for item in config.get('only_jobs', []):
            if item not in self.only_jobs:
                self.only_jobs.append(item)

    @silence_warnings
    def get_jobs(self):
        """Gets all jenkins jobs based on provided filtering."""
        matched_jobs = []

        for only_job in self.only_jobs:
            try:
                job = self.connection.get_job_info(only_job)
                matched_jobs.append(job)
            except jenkins.JenkinsException:
                continue

        if len(matched_jobs) >= 1:
            return matched_jobs

        for job in self.connection.get_jobs():
            keep = False
            # Regex check
            for regex in self.regex_ignore_jobs:
                if re.search(regex, job['name']):
                    keep = True
                    break

            # Static check
            for ignore_job in self.ignore_jobs:
                if ignore_job == job['name']:
                    keep = True
                    break

            if not keep:
                matched_jobs.append(job)

        return matched_jobs

    @silence_warnings
    def calculate_days_since_last_job_build(self):
        """Calculates the number of days since a jobs last build.

        Default behavior will get all jobs from jenkins and determine
        the number of days since their last build.
        """
        for job in self.get_jobs():
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
        print(f"Jenkins jobs last built {self.max_days} days ago")
        for job in self.jobs:
            job_name = job['name']
            days_since_last_build = job['daysSinceLastBuild']

            if days_since_last_build > self.max_days:
                print(f"({days_since_last_build} days) - {job_name}")
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
    "--config-file",
    default=constants.CONFIG_FILE,
    help="Configuration file",
    required=False,
    callback=click_callbacks.ClickFileExist.validate
)
@click.option(
    "--dry-run",
    default=constants.DRY_RUN,
    help="Simulates the actions that would be taken",
    required=False,
    is_flag=True
)
@click.option(
    "--ignore-job",
    help="Filter to ignore job",
    required=False,
    multiple=True
)
@click.option(
    "--job",
    help="Filter to only analyze this job (overrides all filters)",
    required=False,
    multiple=True
)
@click.option(
    "--regex-ignore-job",
    help="Filter to ignore jobs matching regex",
    required=False,
    multiple=True
)
@click.option(
    "--max-days",
    default=constants.MAX_DAYS,
    help="Maximum number of days a job can stick around",
    required=False
)
@click.option(
    "--ssl-verify",
    default=constants.SSL_VERIFY,
    help="Disable SSL verification",
    required=False,
    is_flag=True
)
def cli(jenkins_url, jenkins_username, jenkins_password, config_file, dry_run, ignore_job,
        job, regex_ignore_job, max_days, ssl_verify):
    """Scrub Jenkins Jobs"""
    scrub_jobs = ScrubJobs(
        jenkins_url,
        jenkins_username,
        jenkins_password,
        ssl_verify=ssl_verify,
        dry_run=dry_run,
        max_days=max_days,
        regex_ignore_jobs=regex_ignore_job,
        ignore_jobs=ignore_job,
        config_file=config_file,
        only_jobs=job
    )

    if dry_run:
        print("-- (Simulation Mode) --")

    scrub_jobs.scrub()
