import graphene
from ecommerce.graphene_mutations.user_mutations import \
    AuthMutations
from ecommerce.graphene_mutations.user_mutations import CustomAuthMutations
from graphene.test import Client
from graphene_django.utils.testing import GraphQLTestCase

from users.models import CustomUser


class TestAuthentications(GraphQLTestCase):

    def setUp(self):
        # Given a user with this info,
        CustomUser.objects.create(
            username="khong",
            email="khong@khong.com",
            password="superstrongpassword"
        )


    def test_should_return_valid_token_when_email_enters(self):
        # when they click on a forget password link, an email will be sent
        # through the following mutation,
        class Mutation(CustomAuthMutations, AuthMutations, graphene.ObjectType):
            pass
        schema = graphene.Schema(mutation=Mutation)
        send_email_mutation = """
            mutation{
                sendResetPasswordEmail(email: "khong@khong.com"){
                    token
                    success 
                }
            }
        """
        client = Client(schema)
        result_token = client.execute(send_email_mutation)
        token = result_token["data"]["sendResetPasswordEmail"]["token"]

        # then if the obtained token is valid, we should be able to change the user's password
        # using the built-in passwordReset mutation.
        new_password = "superstrongpassword_2"
        reset_password_mutation = """
            mutation resetPassword($token: String!, $newPassword1: String!, $newPassword2: String!){
                resetPassword(token: $token, newPassword1: $newPassword1, newPassword2: $newPassword2){
                    success
                }
            } 
        """
        variables = {"token": token, "newPassword1": new_password, "newPassword2": new_password } 
        result_password_reset = client.execute(reset_password_mutation, variables=variables)["data"]["resetPassword"]
        #success = true suffice, changing password is already tested: https://github.com/PedroBern/django-graphql-auth/blob/master/tests/test_password_reset.py
        self.assertTrue(result_password_reset["success"])

