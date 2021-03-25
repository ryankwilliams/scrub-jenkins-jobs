"""Click custom callbacks"""

import os

import click

__all__ = [
    "ClickFileExist"
]


class ClickFileExist:
    # pylint: disable=R0903
    """Verifies a file exists for an option accepting a file as input."""

    @staticmethod
    def validate(ctx, param, value):
        #  pylint: disable=W0613
        """Custom validate to verify an option accepting a filename exists."""
        if value:
            if not os.path.isfile(value):
                raise click.BadParameter(f"File {value} does not exist.")
        return value
