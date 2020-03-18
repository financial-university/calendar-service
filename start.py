from os import getenv, getcwd, path

from aiomisc import entrypoint

from app.services import CalendarService, RuzGrabber

config = dict(
    debug=False,
    cache_files_folder=path.join(getcwd(), "ics_folder"),
    files_folder=getenv("API_FILES_FOLDER") or r"c:\\1\\api",
    redis_url=getenv("REDIS_URL") or "redis://localhost/0",
    cache_type="file",
    docker_run=getenv("DOCKER_RUN") or False
)
config["address"] = "0.0.0.0" if config["docker_run"] else "localhost"

if __name__ == "__main__":
    with entrypoint(
        CalendarService(
            address=config["address"],
            port=4040,
            cache_files_folder=config["cache_files_folder"],
            redis_url=config["redis_url"],
            cache_type=config["cache_type"],
        ),
        RuzGrabber(interval=60 * 60 * 24, files_folder=config["files_folder"]),
    ) as loop:
        loop.run_forever()
