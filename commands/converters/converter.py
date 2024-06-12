from abc import ABC, abstractmethod

from pydantic import FilePath, BaseModel


class Converter(ABC, BaseModel):
    @abstractmethod
    def convert(self, pdf_path: FilePath) -> str:
        pass
