# Configuration Files and Registries

We use configuration files and registries to flexibly control the instance initialization. The `Registry` class maps a string to a class, and can build the class given its name and parameters as a dict:

```python
# Register a class

MODELS = Registry('Models')

@MODELS.register()
class MyModel:
    def __init__(self, data):
        self.data = data

# Build an instance using config dict

# You must include MyModel first, this can be done by include MyModel in
# the `__init__.py` file of the project, and then users can just include
# the project to register all models.
import src

config = dict(name='MyModel', data='foo')

mymodel = MODELS.build(config)
```

The configuration files are Python scripts that output one or more `dict` objects for `Registry`. Using a python file to store configurations brings many benefits.

First, it allows flexible inheritance. For example, if I want to change the model in an existing config, I can do it by importing the config dict and then modify the corresponding part, which avoids most boilerplate code:

```python
from existing_config import data, model, feature_extractor

model = dict(name='new_model')
```

Downstreaming scripts will load the components such as `data`, `model`, `feature_extractor` from the configuration file to construct a working pipeline.

Second, a python file allows dynamic configuration such as setting batch size according to the memory of the machine.

Third, parsing a python file does not require written additional parsing code -- just use the `importlib`.
