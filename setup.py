import setuptools

setuptools.setup(
    name="scrub-jenkins-jobs",
    version="0.0.0",
    author="Ryan Williams",
    description="A utility to remove stale Jenkins jobs",
    url="https://github.com/ryankwilliams/scrub-jenkins-jobs",
    packages=setuptools.find_packages(),
    install_requires=[
        "click",
        "python-jenkins",
        "pyyaml"
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    entry_points={
        "console_scripts": [
            "scrub-jenkins-jobs=scrub_jenkins_jobs.scrub:cli"
        ]
    }
)
