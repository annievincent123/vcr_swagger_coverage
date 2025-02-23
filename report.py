from swagger_coverage.src.coverage import SwaggerCoverage 

SWAGGER_URL = 'https://petstore.swagger.io/v2/swagger.json'
STATUS_CODES = [200, 404]

swagger = SwaggerCoverage(
    url=SWAGGER_URL,
    status_codes=STATUS_CODES,
    api_url="https://petstore.swagger.io/",
)
swagger.create_coverage_data()

vcr_file = "petstore_vcr.yml"

swagger.analyze_vcr_file(vcr_file, swagger.swagger_spec)

swagger.create_report()
    