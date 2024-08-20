from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from osm import schemas


class Component(ABC):
    def __init__(self, version: str = "0.0.1"):
        """As subclasses evolve they should keep track of their version."""
        self.version = version
        self.docker_image = None
        self.docker_image_id = None
        self._name = None
        self._orm_model = None

    @abstractmethod
    def run(self, data: Any, **kwargs) -> Any:
        pass

    def _get_model_fields(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
        }

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def orm_model(self) -> schemas.Component:
        if self._orm_model is None:
            self._orm_model = schemas.Component(
                **self._get_model_fields(),
            )
        return self._orm_model

    def model_dump(self) -> dict[str, Any]:
        """Return a dict of the components model."""
        return self.orm_model.model_dump()


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

    def save_file(self, data: str, path: Path):
        self.file_saver.run(data, path)

    def save_json(self, data: dict, path: Path):
        self.json_saver.run(data, path)

    def save_osm(
        self,
        file_in: bytes,
        metrics: dict,
        components: list,
    ):
        # Call the method to save or upload the data
        self.osm_saver.run(file_in, metrics, components)


class Pipeline:
    def __init__(
        self,
        *,
        parsers: list[Component],
        extractors: list[Component],
        savers: Savers,
        filepath: str,
        xml_path: Optional[str] = None,
        metrics_path: Optional[str] = None,
    ):
        self.parsers = parsers
        self.extractors = extractors
        self.savers = savers
        self.filepath = filepath
        self._file_data = None
        self.xml_path = xml_path
        self.metrics_path = metrics_path

    def run(self):
        for parser in self.parsers:
            parsed_data = parser.run(self.file_data)
            if isinstance(parsed_data, str):
                self.savers.save_file(parsed_data, self.xml_path)
            for extractor in self.extractors:
                # extracted_metrics = extractor.run(parsed_data,parser=parser.name)
                extracted_metrics = extractor.run(parsed_data)
                self.savers.save_osm(
                    file_in=self.file_data,
                    metrics=extracted_metrics,
                    components=[*self.parsers, *self.extractors, *self.savers],
                )
                self.savers.save_json(extracted_metrics, self.metrics_path)

    @staticmethod
    def read_file(filepath: str) -> bytes:
        with open(filepath, "rb") as file:
            return file.read()

    @property
    def file_data(self):
        if not self._file_data:
            self._file_data = self.read_file(self.filepath)
        return self._file_data
