from abc import ABC, abstractmethod

from pydantic import BaseModel, FilePath


class Converter(ABC, BaseModel):
    @abstractmethod
    def convert(self, pdf_path: FilePath) -> str:
        pass
