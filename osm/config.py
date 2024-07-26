import os

from dotenv import load_dotenv


class AppConfig:
    """Defaults work with the docker-compose override set up. For improved
    security in production the app container should access the sciencebeam host
    on a docker network"""

    sb_port: int = 8070
    sb_host: str = "sciencebeam"
    sb_protocol: str = "http"

    def __init__(
        self,
        sb_port: int = None,
        sb_host: str = None,
        sb_protocol: str = None,
        vroom_connection_size: int = 2**20,
    ):
        self.sb_port = int(sb_port) if sb_port is not None else self.sb_port
        self.sb_host = sb_host if sb_host is not None else self.sb_host
        self.sb_protocol = sb_protocol if sb_protocol is not None else self.sb_protocol
        self.vroom_connection_size = vroom_connection_size


load_dotenv()
osm_config = AppConfig(
    sb_protocol=os.environ.get("SCIENCEBEAM_PROTOCOL"),
    sb_host=os.environ.get("SCIENCEBEAM_HOST"),
    sb_port=os.environ.get("SCIENCEBEAM_PORT"),
)
