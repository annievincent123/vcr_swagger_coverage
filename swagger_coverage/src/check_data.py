import copy

from requests import Response

import os 


class SwaggerChecker:
    def __init__(self, SwaggerCoverage):
        print(f'================swagger checker init ================')
        self.swaggerCoverage = SwaggerCoverage
        self.swagger_data: dict = self.swaggerCoverage .data.swagger_data
        print(f'check swagger data {self.swaggerCoverage.data.swagger_data}')
        print(f'================s{self.swagger_data} ================')

    def swagger_check(self, key: str, status_code: int, time_execution: float) -> None:
        """
        Try to check response status code and swagger data
        """
        dict_data = copy.deepcopy(self.swagger_data)
        print(f'[[[[[[[[[[[[swagger_check[[[[[[[[[[[')
        print(f'====== key {key} ==========')
        print(f'====== res.status_code {status_code} ==========')
        print(f'====== dict_data {dict_data} ==========')
        print(f'====== time_execution {time_execution} ==========')
        self.swaggerCoverage.data.swagger_data = self._set_check_result(
            key, status_code, dict_data, time_execution
        )
        pass

    @staticmethod
    def _set_check_result(
        key: str, status_code: int, data: dict, time_execution: float
    ) -> dict:
        """
        Set check result
        """
        print(f" 1111111111111111111111111111111_set_check_result_ 1111111{os.getpid()}1111111 ")
        endpoint = data.get(key)
        print(f'endpoint {endpoint}')
        if endpoint:
            if endpoint.get("time_executions") is None:
                endpoint["time_executions"] = [time_execution]
            else:
                t_exc = endpoint.get("time_executions")
                t_exc.append(time_execution)
            statuses = endpoint.get("statuses")
            for status in statuses:
                for key in status.keys():
                    if key == status_code:
                        status[key] = status.get(key, 0) + 1
                        print(f'data {data}')
                        return data
        print(f'data {data}')
        return data
