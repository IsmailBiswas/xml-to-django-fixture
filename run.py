from createfixtures import create_rows_as_dictionaries, create_fixture_output 
from pathlib import Path
from typing import Dict
import os

DATA_DIRECTORY_PATH: Path = Path("./data")
OUTPUT_DIRECTORY_PATH: Path = Path("./output")
DJANGO_APP_NAME = "sedbs"


def get_files(path: Path):
    schema_and_data_file_pair = {}
    files = os.listdir(path)

    for csv_file in files: 
        if csv_file.endswith('.csv'):
            xml_file: str = csv_file[:-4] + ".xml"
            if xml_file in files:
                csv_file_path = Path(os.path.join(path, csv_file))
                xml_file_path = Path(os.path.join(path, xml_file))
                schema_and_data_file_pair[csv_file_path] = xml_file_path
            else:
                print(f"No corresponding xml file found for '{csv_file}' file.")

    if len(schema_and_data_file_pair) ==0:
        raise FileNotFoundError("There no csv file in the './data' folder")

    return schema_and_data_file_pair


if __name__ == "__main__":
    files_dictionary: Dict = get_files(DATA_DIRECTORY_PATH)
    for key in files_dictionary.keys():
        intermidiate_format = create_rows_as_dictionaries(key, files_dictionary[key], DJANGO_APP_NAME)
        output: bytes = create_fixture_output(intermidiate_format)

        output_file: Path = Path(os.path.join(OUTPUT_DIRECTORY_PATH, files_dictionary[key].name))
        if not os.path.exists(output_file.parent):
            os.makedirs(output_file.parent)

        with open(output_file, "wb") as file:
            file.write(output)

        print(f"Done converting: {files_dictionary[key]}")
