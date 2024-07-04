import json
from pathlib import Path

import rpy2.robjects as robjects

from osm.converters.utils import hash_file
from osm.logging.logger import logger


def xml_to_json(md5_pdf_hash, xml_input_path):
    # Load R libraries
    r_library = robjects.r["library"]
    r_library("rtransparent")
    r_library("jsonlite")

    r_rt_all_pmc = robjects.r["rt_all"]
    r_data_frame_to_json = robjects.r["toJSON"]
    try:
        # get current working directory
        cwd = Path.cwd()

        # create a name for the json file
        list_arr = xml_input_path.split("/")
        initial_name = list_arr[len(list_arr) - 1].split(" ")[0]
        if initial_name.split(".xml"):
            initial_name = initial_name.split(".xml")[0]
        output_file_name = initial_name
        for x in list_arr[len(list_arr) - 1].split(" "):
            try:
                if isinstance(int(x), int):
                    output_file_name = f"{initial_name}{x}"
                    break
            except Exception:
                continue

        json_folder_path = cwd / "docs" / "examples" / "rtransparent_json_outputs"

        # check folder exists
        if not json_folder_path.exists():
            json_folder_path.mkdir()

        # Use the rt_all function to extract all indicators and relevant data from the XML file
        xml_data_frame = r_rt_all_pmc(f"{cwd / xml_input_path}")

        # convert data_frame data to json data
        str_vector = r_data_frame_to_json(xml_data_frame, pretty=True)

        json_data = json.loads(f"{str_vector}")
        md5_xml_hash = hash_file(xml_input_path)
        json_data[0]["md5Hashes"] = {
            "originalPdf": md5_pdf_hash,
            "generatedXml": md5_xml_hash,
        }

        with open(file=f"{json_folder_path}/{output_file_name}.json", mode="a") as file:
            file.write(json.dumps(json_data))

        logger.info(
            f"Converted: {xml_input_path} to XML. Output file: {output_file_name}.json"
        )

    except Exception as error:
        # There was an error during the execution of the R script
        logger.error("An error occurred while executing the R script:", exc_info=error)
        logger.error("Request error:", exc_info=error)
