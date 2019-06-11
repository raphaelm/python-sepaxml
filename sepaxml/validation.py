import os


class ValidationError(Exception):
    pass


def is_valid_xml(xmlout, schema):
    import xmlschema  # xmlschema does some weird monkeypatching in etree, if we import it globally, things fail
    my_schema = xmlschema.XMLSchema(os.path.join(os.path.dirname(__file__), 'schemas', schema + '.xsd'))
    return my_schema.is_valid(xmlout.decode())
