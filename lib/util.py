def clean_json_schema(schema):
    """
    JSONスキーマから再帰的に'additionalProperties'と'$schema'を取り除く関数
    """
    if not isinstance(schema, dict):
        return schema

    cleaned_schema = {}

    for key, value in schema.items():
        if key in ["additionalProperties", "$schema"]:
            continue

        if isinstance(value, dict):
            cleaned_schema[key] = clean_json_schema(value)
        elif isinstance(value, list):
            cleaned_schema[key] = [
                clean_json_schema(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            cleaned_schema[key] = value

    return cleaned_schema
