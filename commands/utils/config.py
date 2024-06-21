from pydantic.v1 import BaseSettings


class AppConfig(BaseSettings):
    PORT:int = 8082
    HOST: str = 'localhost'
    PROTOCAL: str = 'http'


config = AppConfig()
