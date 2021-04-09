# Scrub Jenkins Jobs

[![PR-Verification](https://github.com/ryankwilliams/scrub-jenkins-jobs/actions/workflows/pr_verification.yml/badge.svg)](https://github.com/ryankwilliams/scrub-jenkins-jobs/actions/workflows/pr_verification.yml)

A simple command to clean 'scrub' Jenkins jobs.

## Install

```shell
$ virtualenv -p python3.6 scrub-jenkins-jobs
$ source scrub-jenkins-jobs/bin/activate
(scrub-jenkins-jobs) $ pip install git+https://github.com/ryankwilliams/scrub-jenkins-jobs.git
```

## Usage

The example below will scrub all jobs ending in `foo`.

```
# Simulation Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
foo$ --dry-run

# Normal Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
foo$
```
