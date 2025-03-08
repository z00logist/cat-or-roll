import pathlib as pth
import typing as t

from pydantic import Field
from pydantic_settings import BaseSettings


class BaseSettingsConfig(BaseSettings):
    class Config:
        env_nested_delimiter = "__"


class Classifier(BaseSettingsConfig):
    location: pth.Path = Field(
        default=pth.Path.cwd() / "model" / "classifier.pth",
        description="Path to the classifier model.",
    )


class Connection(BaseSettingsConfig):
    host: str = "localhost"
    port: int = 8000
    debug: bool = False


class Configuration(BaseSettingsConfig):
    classifier: Classifier = Classifier()
    connection: Connection = Connection()
    allowed_extensions: t.Sequence[str] = Field(
        default=["png", "jpg", "jpeg"],
        description="Allowed image file extensions"
    )
