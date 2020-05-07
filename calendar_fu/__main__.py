import argparse
import logging
import os
from os import path

import configargparse
from aiomisc import entrypoint

from calendar_fu.services import CalendarService

parser = configargparse.ArgumentParser(
    allow_abbrev=False,
    auto_env_var_prefix="APP_",
    description="iCalendar service for FU RUZ API",
    default_config_files=[
        os.path.join(os.path.expanduser("~"), ".calendar_fa"),
        "/etc/calendar_fa.conf",
    ],
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    ignore_unknown_config_file_keys=True,
)

parser.add_argument("-D", "--debug", action="store_true")

group = parser.add_argument_group("API Options")
group.add_argument("--api-address", default="127.0.0.1")
group.add_argument("--api-port", type=int, default=4040)

group = parser.add_argument_group("Cache")
group.add_argument("--redis", help="Redis url")
group.add_argument("--file", action="store_true", help="Flag for local cache")


def main():
    arguments = parser.parse_args()
    os.environ.clear()
    services = [
        CalendarService(
            address=arguments.api_address,
            port=arguments.api_port,
            cache_files_folder=path.join(os.getcwd(), "ics_folder"),
            redis_url=arguments.redis,
            cache_type=(
                "redis" if arguments.redis else "file" if arguments.file else "no"
            ),
        )
    ]
    with entrypoint(
        *services,
        debug=arguments.debug,
        log_level=logging.DEBUG if arguments.debug else logging.INFO,
    ) as loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
