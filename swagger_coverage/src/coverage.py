from typing import List
import os
import re
import yaml
from urllib.parse import urlparse

from swagger_coverage.src.files import (
    create_dir,
    prepare_path,
    is_file_exist,
    get_json_result_path,
    get_path_to_file,
    load_yaml,
    save_yaml,
)
from swagger_coverage.src.models.swagger_data import SwaggerData
from swagger_coverage.src.results.swagger_results import SwaggerResults
from swagger_coverage.src.results.load_results import LoadSwaggerResults
from swagger_coverage.src.singltone_like import Singleton
from swagger_coverage.src.report.html.html_report import HtmlReport
from swagger_coverage.src.prepare_data import PrepareData
from swagger_coverage.src.requests import load_swagger, get_swagger_spec
from swagger_coverage.src.check_data import SwaggerChecker


_SWAGGER_REPORT_DIR = "swagger_report"
_TEST_SWAGGER_FILE_NAME = "data_swagger.yaml"

SWAGGER_URL = 'https://petstore.swagger.io/v2/swagger.json'


class SwaggerCoverage(metaclass=Singleton):
    def __init__(
            self,
            url: str = None,
            urls: List[str] = None,
            api_url: str = None,
            status_codes: List[int] = None,
            path: str = _SWAGGER_REPORT_DIR,
    ):
        self.api_url = api_url
        self.swagger_url = self._select_urls(url, urls)
        self.data = SwaggerData()
        self.path = prepare_path(path=path, report_dir=_SWAGGER_REPORT_DIR)
        self.swagger_spec = get_swagger_spec(SWAGGER_URL)
        if status_codes is None:
            self.status_codes = _DEFAULT_STATUS_CODE
        else:
            self.status_codes = [int(s) for s in status_codes]
        print(f'******************** SwaggerCoverage >>>>>>>>>{os.getpid()}>>>>>>>>>')
        
    def _select_urls(self, url: str, urls: str):
        if url:
            return [url]
        if urls:
            return urls
        return None
        
    def create_coverage_data(self, file_name: str = _TEST_SWAGGER_FILE_NAME):
        """
        Create coverage data
        """
        create_dir(self.path)
        self.path_to_file = get_path_to_file(self.path, file_name)
        print(f' ############ create_coverage_data exist file  ###########{self.path_to_file}')
        if not is_file_exist(path=self.path_to_file):
            load_data = load_swagger(self.swagger_url)
            print(f'load_data {load_data}')
            prepare = PrepareData()
            print(f'load_data {prepare}')
            prepare_data = prepare.prepare_swagger_data(
                data=load_data, status_codes=self.status_codes
            )
            save_yaml(path_file=self.path_to_file, data=prepare_data)
        self._prepare_exist_swagger()
        
    def _prepare_exist_swagger(self):
        dict_data = load_yaml(path_to_file=self.path_to_file)
        prepare = PrepareData()
        self.data.swagger_data = prepare.prepare_check_file_data(dict_data)
        
    def save_results(self) -> str:
        results = SwaggerResults(self)  # <- SELF == SwaggerCoverage OBJECT
        return results.save_results(self.path)

    def create_report(self, path=_SWAGGER_REPORT_DIR, report_type="html"):
        # merge results
        result_path = f"{path}/json_results"
        if not is_file_exist(result_path):
            create_dir(self.path)
        self.save_results()
        result_paths = get_json_result_path(path=result_path)
        load_results = LoadSwaggerResults()
        merge_result = load_results.merge_results(result_paths)
        # create report
        report = HtmlReport(merge_result)
        report.create(path)
        
    def find_operation_id(self, swagger_spec, path, method):
        """Find the operation ID for a given path and method"""
        # Normalize the path by removing the base path
        base_path = swagger_spec.get('basePath', '')
        normalized_path = path.replace(base_path, '')
        
        # Convert path parameters from actual values to Swagger format
        # e.g., /pet/12345 -> /pet/{petId}
        path_pattern = re.sub(r'/\d+', '/{petId}', normalized_path)
        
        # Check if the path exists in the swagger spec
        for spec_path, methods in swagger_spec['paths'].items():
            # Convert swagger path parameters to regex pattern
            spec_pattern = re.sub(r'\{[^}]+\}', '[^/]+', spec_path)
            if re.match(f"^{spec_pattern}$", path_pattern):
                if method.lower() in methods:
                    return methods[method.lower()].get('operationId')
        return None
        
        
    def analyze_vcr_file(self, vcr_yaml_path, swagger_spec):
        """Analyze VCR file and extract operation IDs, status codes, and execution times"""
        with open(vcr_yaml_path, 'r') as f:
            vcr_data = yaml.safe_load(f)
        
        results = []
        
        for interaction in vcr_data['interactions']:
            request = interaction['request']
            response = interaction['response']
            
            # Extract request details
            method = request['method']
            uri = request['uri']
            path = urlparse(uri).path
            
            # Find operation ID
            operation_id = self.find_operation_id(swagger_spec, path, method)
            
            # Get status code
            status = response['status']
            
            # Calculate execution time (in real VCR files this would come from recorded data)
            # Here we'll set a placeholder value
            execution_time = 0.5  # seconds
            
            results.append({
                'operation_id': operation_id,
                'path': path,
                'method': method,
                'status': status,
                'execution_time': execution_time
            })
        
        self.call_swagger_checker(results)
        
    def call_swagger_checker(self, results):
        print(f'call_swagger_checker {results}')
        for item in results:
            try:
                print(f"SwaggerChecker {item['operation_id']} {item['status']} {item['execution_time']} -{os.getpid()} -----------" )
                SwaggerChecker(self).swagger_check(item['operation_id'], item['status'], item['execution_time'])
                print(f"SwaggerChecker done {item['operation_id']}")
            except AttributeError:
                print(f"AttributeError {item['operation_id']}")

    