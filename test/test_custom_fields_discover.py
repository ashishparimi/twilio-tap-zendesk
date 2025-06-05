import tap_tester.menagerie   as menagerie
import singer
from base import ZendeskTest

class ZendeskCustomFieldsDiscover(ZendeskTest):
    def name(self):
        return "tap_tester_zendesk_custom_fields_discover"

    def do_test(self, conn_id):
        # Get the Streams for Organizations and Users
        streams = [c for c in self.found_catalogs if c['stream_name'] in ['organizations', 'users']]

        # Create an array of arrays where the first element is the word minus the last letter ie: "organization"
        # and the second element is the annotated schema
        schemas = [(s['stream_name'][:-1], menagerie.get_annotated_schema(conn_id, s['stream_id'])) for s in streams]

        # Loop over them
        for schema in schemas:
            properties = schema[1]['annotated-schema']['properties']
            fields_properties = properties.get('{}_fields'.format(schema[0]), {}).get('properties', {})
            
            # Ensure that "organization_fields" or "user_fields" are objects in the annotated schema
            # with their own set of properties
            self.assertIsNotNone(fields_properties,
                                msg='{}_fields not present in schema!'.format(schema[0]))
            
            # Verify that all custom fields have valid types
            for field_name, field_schema in fields_properties.items():
                # Check that the field has a type property
                self.assertIn('type', field_schema, 
                            msg=f'Field {field_name} missing type definition')
                
                # Verify that the type is either a string or array (for multiselect)
                field_type = field_schema['type']
                if isinstance(field_type, list):
                    # For fields that can be null
                    self.assertTrue(any(t in ['string', 'array', 'integer', 'number', 'boolean'] for t in field_type),
                                  msg=f'Field {field_name} has invalid type: {field_type}')
                else:
                    self.assertIn(field_type, ['string', 'array', 'integer', 'number', 'boolean'],
                                msg=f'Field {field_name} has invalid type: {field_type}')

