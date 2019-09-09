import os


class ValidationError(Exception):
    pass


def try_valid_xml(xmlout, schema):
    import xmlschema  # xmlschema does some weird monkeypatching in etree, if we import it globally, things fail
    try:
        my_schema = xmlschema.XMLSchema(os.path.join(os.path.dirname(__file__), 'schemas', schema + '.xsd'))
        my_schema.validate(xmlout.decode())

    except xmlschema.XMLSchemaValidationError as e:
        raise ValidationError(
            "The output SEPA file contains validation errors. This is likely due to an illegal value in one of "
            "your input fields."
        ) from e
