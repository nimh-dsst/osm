import os

import requests


def _upload_data(args, file_in, xml, extracted):
    osm_api = os.environ.get("OSM_API", "http://localhost:80")

    # Send POST request to OSM API
    response = requests.put(
        f"{osm_api}/upload",
        json={
            "osm_version": "1.0",
            "user_comment": "example_comment",
        },
    )
    # "work": {
    #     "user_defined_id": args.uid,
    #     "pmid": "pmid_example",
    #     "doi": "doi_example",
    #     "openalex_id": "openalex_example",
    #     "scopus_id": "scopus_example",
    #     # "file": file_in,
    #     "content_hash": hashlib.sha256(file_in).hexdigest(),
    # },
    # "metrics": extracted,

    # Check response status code
    if response.status_code == 200:
        print("Invocation data uploaded successfully")
    else:
        print("Failed to upload invocation data")
