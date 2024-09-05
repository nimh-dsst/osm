import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from osm import schemas
from osm.db import db_init


class Component(ABC):
    def __init__(self, version: str = "0.0.1"):
        """As subclasses evolve they should keep track of their version."""
        self.version = version
        self.docker_image = None
        self.docker_image_id = None
        self._name = None
        self._orm_model = None

    @abstractmethod
    def _run(self, data: bytes | dict, **kwargs) -> Any:
        """Abstract method that subclasses must implement."""
        pass

    def run(self, data: bytes, *args, **kwargs) -> Any:
        print(f"{self.name} (version {self.version}) is running.")
        return self._run(data, *args, **kwargs)

    def _get_orm_fields(self) -> dict[str, Any]:
        fields = {}
        for fieldname in self.orm_model_class.model_fields.keys():
            if hasattr(self, fieldname):
                fields[fieldname] = getattr(self, fieldname)

        return fields

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def orm_model_class(self) -> type:
        return schemas.Component

    @property
    def orm_model(self) -> schemas.Component:
        self._orm_model = self.orm_model_class(
            **self._get_orm_fields(),
        )
        return self._orm_model

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        """Return a dict of the components model."""
        return self.orm_model.model_dump(*args, **kwargs)


class Savers:
    def __init__(
        self, file_saver: Component, json_saver: Component, osm_saver: Component
    ):
        self.file_saver = file_saver
        self.json_saver = json_saver
        self.osm_saver = osm_saver

    def __iter__(self):
        yield self.file_saver
        yield self.json_saver
        yield self.osm_saver

    def save_file(self, data: bytes, path: Path):
        self.file_saver.run(data, path=path)

    def save_json(self, data: dict, path: Path):
        self.json_saver.run(data, path=path)

    def save_osm(
        self,
        data: bytes,
        metrics: dict,
        components: list,
    ):
        # Call the method to save or upload the data
        self.osm_saver.run(data, metrics=metrics, components=components)


class Pipeline:
    def __init__(
        self,
        *,
        parsers: list[Component],
        extractors: list[Component],
        savers: Savers,
        input_path: str,
        xml_path: Optional[str] = None,
        metrics_path: Optional[str] = None,
    ):
        self.parsers = parsers
        self.extractors = extractors
        self.savers = savers
        self.input_path = input_path
        self._file_data = None
        self.xml_path = xml_path
        self.metrics_path = metrics_path

    def run(self, user_managed_compose: bool = False, llm_model: str = None):
        try:
            asyncio.run(db_init())
        except Exception as e:
            print(e)
            raise EnvironmentError("Could not connect to the OSM database.")
        for parser in self.parsers:
            parsed_data = parser.run(
                self.file_data, user_managed_compose=user_managed_compose
            )
            if isinstance(parsed_data, bytes):
                self.savers.save_file(parsed_data, self.xml_path)
            for extractor in self.extractors:
                extracted_metrics = extractor.run(
                    parsed_data, parser=parser.name, llm_model=llm_model
                )
                self.savers.save_osm(
                    data=self.file_data,
                    metrics=extracted_metrics,
                    components=[parser, extractor, *self.savers],
                )
                self.savers.save_json(extracted_metrics, self.metrics_path)

    @staticmethod
    def read_file(input_path: str) -> bytes:
        with open(input_path, "rb") as file:
            return file.read()

    @property
    def file_data(self):
        if not self._file_data:
            self._file_data = self.read_file(self.input_path)
        return self._file_data
