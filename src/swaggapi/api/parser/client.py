
import yaml
import requests
from cached_property import cached_property
from swaggapi.api.openapi.models import OpenAPI, Referance


class Operation(object):

    def __init__(self, base_url, uri, method, descriptor):
        self.uri = uri
        self.base_url = base_url
        self.method = method
        self.descriptor = descriptor

    def __call__(self, *args, **kwargs):
        response = requests.request(method=self.method,
                                    url="{base_url}{uri}".format(
                                        base_url=self.base_url,
                                        uri=self.uri
                                    ), json=kwargs)
        return response

    @cached_property
    def parameters(self):
        if self.descriptor.parameters is not None:
            return [parameter.name for parameter in self.descriptor.parameters]

        return []


class SwaggAPI(object):
    def __init__(self, swagfile):
        self.swag = OpenAPI.decode(swagfile)

    @cached_property
    def servers(self):
        return [server.url for server in self.swag.servers]

    @cached_property
    def base_url(self):
        return self.servers[0]

    def __dir__(self):
        res = dir(type(self)) + list(self.__dict__.keys())
        res.extend([operation for operation in self.operations.keys()])
        return res

    def __getattr__(self, item):
        return self.operations[item]

    @cached_property
    def operations(self):
        return {operation.operationId: Operation(uri=path,
                                                 base_url=self.base_url,
                                                 method=method,
                                                 descriptor=operation)
                for path in self.swag.paths
                for method, operation in self.swag.paths[path].methods.items()}


if __name__ == '__main__':
    with open("pet.yaml") as f:
        test = SwaggAPI(yaml.load(f))

    import ipdb; ipdb.set_trace()
