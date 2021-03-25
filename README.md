# Scrub Jenkins Jobs

A simple command to clean 'scrub' Jenkins jobs.

## Install

```shell
$ virtualenv -p python3.6 scrub-jenkins-jobs
$ source scrub-jenkins-jobs/bin/activate
(scrub-jenkins-jobs) $ pip install git+https://github.com/ryankwilliams/scrub-jenkins-jobs.git
```

## Usage

### Clean All

```
# Simulation Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--dry-run

# Normal Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD
```

### Clean Jobs > 7 days

```
# Simulation Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--dry-run --max-days 7

# Normal Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--max-days 7
```

### Clean A Specific Job

*This overrides all other filters!*

```
# Simulation Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--dry-run --job job-123

# Normal Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--job job-123
```

### Clean All Jobs Ignorning Ones Matching Regex

```
# Simulation Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--dry-run --regex-ignore-job foo$

# Normal Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--regex-ignore-job foo$
```

### Clean All Jobs Ignoring Specific Jobs

```
# Simulation Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--dry-run --ignore-job job-123

# Normal Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--ignore-job job-123
```

### Using A Configuration File

```
cat .scrub-jenkins-jobs
---
regex_ignore_jobs:
  - foo-*
  - bar$

ignore_jobs:
  - job-123

only_jobs: []
```

```
# Simulation Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--dry-run --config-file .scrub-jenkins-jobs

# Normal Mode
(scrub-jenkins-jobs) $ scrub-jenkins-job JENKINS_URL JENKINS_USERNAME JENKINS_PASSWORD \
--config-file .scrub-jenkins-jobs
```
