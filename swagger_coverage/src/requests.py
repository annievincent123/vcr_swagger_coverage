import logging

import requests

import yaml

from swagger_coverage.src.models.swagger_data import SwaggerResponse

logger = logging.getLogger("swagger")


def load_swagger(urls) -> SwaggerResponse:
    """
    Load and get swagger data
    """
    path_data = []
    for url in urls:
        logger.info(f"Start load swagger {url}")
        res = requests.get(url)
        if res.status_code == 200:
            try:
                data = yaml.safe_load(res.text)
                path_data.append(data.get("paths"))
            except Exception:
                raise ValueError("Couldn't load yaml")
        else:
            logger.error(f"Couldn't get the file, status code is {res.status_code}")
    merged_dict = {}

    for d in path_data:
        merged_dict = {**merged_dict, **d}
    type_swagger = 'swagger'  # FIXME
    return SwaggerResponse(paths=merged_dict, swagger_type=type_swagger)
    
def get_swagger_spec(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for HTTP errors
        swagger_json = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Swagger JSON: {e}")
        
    return swagger_json
