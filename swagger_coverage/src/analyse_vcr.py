import yaml
import json
import re
from urllib.parse import urlparse
from datetime import datetime

def load_swagger_spec(swagger_content):
    """Load and parse Swagger specification"""
    if isinstance(swagger_content, str):
        return json.loads(swagger_content)
    return swagger_content

def find_operation_id(swagger_spec, path, method):
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

def analyze_vcr_file(vcr_yaml_path, swagger_spec):
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
        operation_id = find_operation_id(swagger_spec, path, method)
        
       
        # Calculate execution time (in real VCR files this would come from recorded data)
        # Here we'll set a placeholder value
        execution_time = 0.5  # seconds
        
        results.append({
            'operation_id': operation_id,
            'path': path,
            'method': method,
            'response': response,
            'execution_time': execution_time
        })
    
    return results

def print_analysis_report(results):
    """Print a formatted analysis report"""
    print("\nVCR Analysis Report")
    print("-" * 80)
    print(f"{'Operation ID':<30} {'Method':<8} {'Status':<8} {'Time (s)':<10}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['operation_id']:<30} "
              f"{result['method']:<8} "
              f"{result['status']:<8} "
              f"{result['execution_time']:<10.3f}")

def main():
    # In a real scenario, these would be command line arguments
    vcr_file = "petstore_vcr.yml"
    swagger_file = "swagger.json"
    
    # Load Swagger specification
    with open(swagger_file, 'r') as f:
        swagger_spec = json.load(f)
    
    # Analyze VCR file
    results = analyze_vcr_file(vcr_file, swagger_spec)
    
    # Print report
    print_analysis_report(results)
    
    # Calculate summary statistics
    total_time = sum(r['execution_time'] for r in results)
    success_count = sum(1 for r in results if 200 <= r['status'] < 300)
    
    print("\nSummary:")
    print(f"Total Requests: {len(results)}")
    print(f"Successful Requests: {success_count}")
    print(f"Total Execution Time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()