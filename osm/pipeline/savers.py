import json

from .core import Saver


class FileSaver(Saver):
    def save(self, data: str):
        with open("output.xml", "w") as file:
            file.write(data)


class JSONSaver(Saver):
    def save(self, data: dict):
        with open("output.json", "w") as file:
            json.dump(data, file)


class OSMSaver(Saver):
    def save(self, data: dict):
        # Assuming there's a method to post data to an endpoint
        response = self.post_to_osm(data)
        if response.status_code != 200:
            raise Exception("Failed to save metrics to OSM")

    def post_to_osm(self, data: dict):
        # Mock implementation: Replace with actual HTTP request
        print(f"Posting to OSM: {data}")
        # TODO
        pass
