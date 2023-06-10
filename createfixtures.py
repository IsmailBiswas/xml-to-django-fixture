import xml.etree.ElementTree as ET
from typing import List, Dict 
from pathlib import Path
import csv

def get_schema_as_a_list(FilePath: Path) -> List[List]:
    """
    Every columns properties like Table_name, column_name, data_type,
    is_nullable, length are returned in list of list. 
    """
    with open(FilePath, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        return list(csvreader) 

def create_rows_as_dictionaries(csv_schema_file: Path, xml_data_file: Path, django_app_name: str) -> list[dict[str, str]]:
    """
    This function reads the schema from the CSV file and return a list of 
    dictionaries where each dictionary represents a row of data.

    :param csv_schema_file: The file path of the CSV schema.
    :type csv_schema_file: str

    :param xml_data_file: The file path of the XML data.
    :type xml_data_file: str

    :param django_app_name: The name of the Django app that the data will be used in.
    :type django_app_name: str

    :return: A list of dictionaries, where each dictionary represents a row of data.
    :rtype: list
    """

    rows = []
    tree = ET.parse(xml_data_file)
    root = tree.getroot()
    schema_as_a_list = get_schema_as_a_list(csv_schema_file)

    for row_element in root.findall(".//row"):
        row = {}
        row["model"] = str(django_app_name + '.' + schema_as_a_list[1][0])
        row["pk"] = row_element.attrib["Id"]

        for field in schema_as_a_list[1:]:
            try:
                row[field[1]] = row_element.attrib[field[1]]
            except KeyError:
                if field[1] != "Id (PK)":
                    row[field[1]] = None
        rows.append(row)
    print(rows)
    return rows


def create_fixture_output(row_data_as_dictionary: List[Dict[str, str]]) -> bytes:
    """This function takes a list of dictionaries where each dictionary 
    represents a row of data and returns Django fixture xml serializer 
    formatted string byte data.

    :param row_data_as_dictionary: A dictionary whose each key value pair represents a column for a row.
    :type row_data_as_dictionary: Dict

    :return: Django fixture xml serializer format data as a string byte. 
    :rtype: str
    """

    output_data = ET.Element("django-objects")
    for field_data in row_data_as_dictionary:
        data_element = ET.SubElement(output_data, "object")
        for key in field_data.keys():
            if key == "model":
                data_element.attrib.update({"model": str(field_data[key])})
            elif key == "pk":
                data_element.attrib.update({"pk": str(field_data[key])})
            else:
                if field_data[key] != None:
                    field_element = ET.SubElement(data_element, "field")
                    field_element.attrib.update({"name": key})
                    field_element.text = str(field_data[key])

    return ET.tostring(output_data, encoding="utf-8")


if __name__ == "__main__":
    data_file_path: Path = Path("./Tags.xml")
    csv_schema_file_path: Path = Path("./Tags.csv")
    django_app_name = "sedbs"

    rows_as_python_dictionaries = create_rows_as_dictionaries(csv_schema_file_path, data_file_path, django_app_name)
    fixture_output = create_fixture_output(rows_as_python_dictionaries)

    output_file = "./modified_my_script_output.xml"
    with open(output_file, "wb") as file:
        file.write(fixture_output)

    print(f"Successfully converted to Django fixtures XML serialization format. Output file: {output_file}")

