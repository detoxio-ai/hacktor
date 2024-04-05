import logging
from urllib.parse import urlparse
from gradio_client import Client

class GradioUtils:

    def is_gradio_endpoint(self, url):
        url = self.normalize_url(url)
        try:
            logging.debug("Checking if url is a gradio endpint")
            _client = Client(url, verbose=False)
            return True
        except Exception as ex:
            logging.debug("Received while connecting to client %s", ex)
            return False

    def parse_api_signature(self, url, fuzz_marker):
        try:
            api_name, gr_parameters = self._get_predict_api_specs(url)
            if not api_name:
                return None, None
            
            parameters = []
            for i, gr_p in enumerate(gr_parameters):
                if i == 0:
                    parameters.append(fuzz_marker)
                else:
                    dv = None
                    if gr_p["has_default_value"]:
                        dv = gr_p["default_value"]
                    else:
                        if gr_p['python_type'] == 'str':
                            dv = ""
                        else:
                            dv = 0
                    parameters.append(dv)
                            
            return api_name, parameters
        except Exception as ex:
            logging.exception(ex)
        return None, None
            
    def normalize_url(self, url):
        # if it huggingface space
        hf_space_name = self._extract_hugging_face_space_name(url)
        if hf_space_name:
            return hf_space_name
        return url
        
    def _get_predict_api_specs(self, url):
        for api_name, parameters in self._enumerate_api_specs(url):
            if "lambda" in api_name.lower():
                continue
            # '/predict', 
            #[
            #   {'name': 'prompt', 'has_default_value': False, 'default_value': None, 'python_type': 'str'},
            #   {'name': 'input', 'has_default_value': False, 'default_value': None, 'python_type': 'str'}, 
            #   {'name': 'history', 'has_default_value': True, 'default_value': [], 'python_type': 'Tuple[str | Dict(file: filepath, alt_text: str | None) | None, str | Dict(file: filepath, alt_text: str | None) | None]'}
            # ]
            return api_name, parameters
        return None, None

    def _client(self, url):
        url = self.normalize_url(url)
        client = Client(url, verbose=False)
        return client

    def _enumerate_api_specs(self, url):
        client = self._client(url)
        named_endpoints_dict = client.view_api(print_info=False, return_format="dict")['named_endpoints']
        yield from self._parse_api_specs_2_named_endpoints(named_endpoints_dict)

    def _parse_api_specs_2_named_endpoints(self, named_endpoints_dict):
        for name, details in named_endpoints_dict.items():
            if details.get('parameters'):
                #[
                #   {'name': 'prompt', 'has_default_value': False, 'default_value': None, 'python_type': 'str'},
                #   {'name': 'input', 'has_default_value': False, 'default_value': None, 'python_type': 'str'}, 
                #   {'name': 'history', 'has_default_value': True, 'default_value': [], 'python_type': 'Tuple[str | Dict(file: filepath, alt_text: str | None) | None, str | Dict(file: filepath, alt_text: str | None) | None]'}
                # ]
                f = self._extract_api_info(details.get('parameters'))
                yield(name, f)
    
    def _extract_api_info(self, data):
        api_name = data[0]['label']
        parameters = []
        for param in data:
            parameter_info = {
                'name': param['parameter_name'],
                'has_default_value': param['parameter_has_default'],
                'default_value': param['parameter_default'],
                'python_type': param['python_type']['type']
            }
            parameters.append(parameter_info)
        return parameters
    
    def _extract_hugging_face_space_name(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_segments = parsed_url.path.split('/')
        
        if domain == 'huggingface.co' and len(path_segments) >= 3:
            orgname = path_segments[-2]
            app = path_segments[-1] 
            return f"{orgname}/{app}"
        else:
            return ""
