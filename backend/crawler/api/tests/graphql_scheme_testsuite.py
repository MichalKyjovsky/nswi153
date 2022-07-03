import json
from graphene_django.utils.testing import GraphQLTestCase
from ..schema import schema


class SchemaTestCase(GraphQLTestCase):

    def setUp(self) -> None:
        super().setUp()

    GRAPHQL_URL = '/graphql'
    GRAPHQL_SCHEMA = schema

    def test_web_page_query(self):
        response = self.query(
            '''
            query {
              websites {
                id
                label
                url
                regex
                tags {
                  tag
                }
                active
              }
            }
            '''
        )

        content = json.loads(response.content)

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # TODO: Add content comparison

    def test_query_with_parameters(self):
        response = self.query(
            '''
            query {
               nodesByIds(webPages: [5, 6]) {
                url,
                title,
                crawlTime,
                owner {
                  id,
                  url,
                  label,
                  interval,
                  active
                },
                links {
                  title
                }
              }
            }
            '''
        )

        content = json.loads(response.content)

        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # TODO: Add content comparison
