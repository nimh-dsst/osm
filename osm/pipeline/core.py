from abc import ABC, abstractmethod
from typing import Optional


# Parser Interface
class Parser(ABC):
    @abstractmethod
    def parse(self, data: bytes) -> str:
        pass


# Extractor Interface
class Extractor(ABC):
    @abstractmethod
    def extract(self, data: str) -> dict:
        pass


# Saver Interface
class Saver(ABC):
    @abstractmethod
    def save(self, data: dict):
        pass


class Savers:
    def __init__(self, file_saver: Saver, json_saver: Saver, osm_saver: Saver):
        self.file_saver = file_saver
        self.json_saver = json_saver
        self.osm_saver = osm_saver

    def save_file(self, data: str):
        self.file_saver.save(data)

    def save_json(self, data: dict):
        self.json_saver.save(data)

    def save_osm(self, data: dict):
        self.osm_saver.save(data)


class Pipeline:
    def __init__(
        self,
        *,
        parsers: list[Parser],
        extractors: list[Extractor],
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
            parsed_data = parser.parse(self.file_data)
            if isinstance(parsed_data, str):
                self.savers.save_file(parsed_data, self.xml_path)
            for extractor in self.extractors:
                extracted_metrics = extractor.extract(parsed_data)
                self.savers.save_osm(
                    {
                        "parser": parser.__class__.__name__,
                        "extractor": extractor.__class__.__name__,
                        "metrics": extracted_metrics,
                    }
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
