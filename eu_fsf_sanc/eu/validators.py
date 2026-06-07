class SchemaValidationError(Exception):
    pass


def validate_item(item):
    if not item["name"]:
        raise SchemaValidationError("Missing name")

    item["sanctions"] = item.get("sanctions", "")
    item["aliases"] = item.get("aliases", "")

    return item
