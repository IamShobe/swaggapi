# swaggapi

Swagger **OpenAPI 3** wrapper for Python.

This package has the vision of making REST api usage and access - better, faster and easier.
For this purpose, you will have to setup few models and "tell" the system what is the structure of each of 
your requests and responses.

This  Python lib will also build automatically swagger.json file which can later  on be displayed using 
**Swagger UI**.

Features:
  - Client and Server rest usage.
  - Dynamically generate swagger file.
  - Validate input parameters and output responses.
## Build your models
### Models
First, each of your uri methods ("post", "get", "patch", etc..) has to have a model which represents it.
The model class - 
```Python
class AbstractAPIModel(object):  
  TITLE = None  
  PROPERTIES = []  
  EXAMPLE = None  
```
Your model should inherit from this object.
Examples:
```Python
class GenericModel(AbstractAPIModel):  
  """This is an empty model."""
  TITLE = "Generic Object"  
  PROPERTIES = []  
  EXAMPLE = {}
```
```Python
class CatModel(AbstractAPIModel):  
  TITLE = "Cat"  
  PROPERTIES = [  
        NumberField(name="id"),  
        StringField(name="name"),    
        ArrayField(name="friends_ids", items_type=int)
  ]
  EXAMPLE = {
     "id": 0,
     "name": "Garfield",
     "friends_ids": [1, 3]
  }
```
Class Attributes:
 - TITLE (str)  - the name of the model, if not set  - the class name is taken by default.
 - PROPERTIES (list) - list of **fields** that will represent the model structure.
 - EXAMPLE (object) - any kind of json serializeable object.
 - \_\_doc\_\_ (str)  - the object description.

###  Response
The response type  should also  be represented as the model does.
```Python
class EmptyResponse(AbstractResponse):  
  """This is an empty response."""
  PROPERTIES = []
```

### Fields

Right now there are 5 types of supported fields:
Each field has the following properties:
```Python
class Field(object):  
  def __init__(self, name, type, description="", required=False, 
               example=None, location="body", deprecated=False)
```
Instance  Attributes:
 - name (str) - the name of the field.
 - required  (bool) - if the field is required or not (default:  False).
 - type (str) - string that represents the type of the field.
 - description (str) - the field's description.
 - example (object) - example of a valid object of the field.
 - location (str)  - where the field is passed from - possibilities -  ["body", "query", "header", "path",  "cookie"].
 - deprecated (bool) - whether the field is deprecated or not.

If you want to create your own field type,  you can  expand the following methods - 
```Python
def default_example(self):  
  """Example in case field didn't specify a unique example."""
  return  
  
def examples(self, schema_bank, index):
  """In case of complex types field - how should the example be generated."""
  return Example(value=self.example)  
  
def schemas(self, schema_bank, index):  
  """In case of complex types field - how does the schema should be gennerated."""
  example_ref = get_schema(self, schema_bank, "examples")  
    example = schema_bank[example_ref.type][example_ref.reference]  
    return Schema(title=self.name, type=self.type,  
  description=self.description,  
  example=example.value,  
  deprecated=self.deprecated)
```
Ready To Go Field Types:
``ArrayField``,  ``StringField``, ``BoolField``,  ``NumberField``, ``ModelField``.

## Build Your Requests

```Python
class Request(object):  
    URI = None  
    DEFAULT_MODEL = None  
    DEFAULT_RESPONSES = {}  
    PARAMS_MODELS = {  
       "get": None,  
       "post": None,  
       "delete": None,  
       "put": None,  
       "head": None,  
       "patch": None,  
       "trace": None,  
    }  
    RESPONSES_MODELS = {  
       "get": None,  
       "post": None,  
       "delete": None,  
       "put": None,  
       "head": None,  
       "patch": None,  
       "trace": None,  
    }  
    TAGS = {  
        "get": [],  
        "post": [],  
        "delete": [],  
        "put": [],  
        "head": [],  
        "patch": [],  
        "trace": [],  
    }  
```
Each request should specify the models of each of the methods.
If the request uses a default model you can use the *default* class  attributes for convinence.
Tags  - are a way to group together responses  method.

###  Django Integration
For this purpose,  there  is a new defined classes -  
```Python
class DjangoRequestView(View, Request)
class Response(JsonResponse)
class BadRequest(Exception)
class ServerError(Exception)
```

 - BadRequest - will return httplib.BadRequest status code with the exception details inserted within it.
```Python
 raise BadRequest({"details": "Invalid Request"})
```
 - Response - For the validation of the params with the specified model,  you should use Response instead of
	 Django's  JsonResponse.
```Python
return Response({"properties": properties}, status=httplib.OK)
```
- DjnagoRequestView - each of your  views should inherit from this class.
this class  inherits from  the  ```Request``` object specified  above,  so everything until now is the same,
make  sure to fill the required models  if their method implemented.
```Python
class GetCats(DjangoRequestView):  
  """Get all the cats stored in the system that match the needed query."""  
  URI = "get_cats"  
  DEFAULT_MODEL = CatsDescriptorModel  
  DEFAULT_RESPONSES = {  
        httplib.OK: CatsModel,  
        httplib.BadRequest: NoCatsFoundModel,
  }  
  TAGS = {  
     "post": ["Cats"]  
  }
  # default params are taken because no specific model for this method
  def post(self,  request,  *args,  **kwargs):
      ...
	  return Response({...}, httplib.OK)
```

  -  ServerError - thrown when exception occured  within the view.
 
 
## Swagger File Generation
Now when  everything is ready we can generate our first swagger file!

### Django 
Application's  ``urls.py``  file
```Python 
from swagapi.build import Swagger
from swagapi.api.openapi.models import Info, License, Tag

requests = [GetCats]  
  
info = Info(title="Cats OpenAPI",  
            version="0.1.0",  
            description="Cats Swagger for cats management",  
            license=License(name="MIT"))
tags = [Tag(name="Cats",  description="All requests for managing cats")]  
# don't forget to configure the mount_url - all the uri until the current file
swagger = Swagger(info, mount_url="api", requests=requests, tags=tags)  
  
  
def swagger_file(request, *args, **kwargs):
    """We dynamically generate the swagger file."""
    swagger.configure_base_url(request)  
    return JsonResponse(swagger.api.json(), status=httplib.OK)  
  
  
def index(request, *args, **kwargs):
  """Here we use static deploy for Swagger UI."""
  return render(request, "swagger.html")  
  
  
urlpatterns = patterns("",  
  url("^$", index),  
  url("^swagger.json$", swagger_file),  
  *swagger.get_django_urls()  # here all requests uris are automatically built.
)
```

## Client  Usage

Simply create  a requester - 
```Python
requester = Requester(host=host,  
  port=port,  
  base_url=self.base_uri,  # Where the api swagger is mounted.
  logger=self.logger)  # optional
```
And  call your request -
```Python
request_data = CatsDescriptorModel({   # request parameters
    "cats_ids": [1, 2] 
})  
response = self.requester.request(GetCats,  # rememebr the request class name
  data=request_data,  
  method="post")

# type(response)  == CatsModel if success, NoCatsFoundModel if failed!
```