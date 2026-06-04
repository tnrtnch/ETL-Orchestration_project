import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError


with open('kaldata/content.json') as f:
    content = json.load(f)

with open('kaldata/content-schema.json') as f:
    schema = json.load(f)



try:
    validate(instance=content, schema=schema)
    print("Validation succeeded!")

except ValidationError as e:
    print("Validation failed!")
    print(f"Error message: {e.message}")