import yaml

from swaggapi.api.openapi.models import OpenAPI, Referance

def main():
    with open("pet.yaml") as f:
        swagfile = yaml.load(f)
    test = OpenAPI.decode(swagfile)
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main()

