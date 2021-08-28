import graphene
from graphene import ObjectType
from graphql_auth import mutations
from users.models import CustomUser
from graphql_auth.utils import get_token


class ValidateEmailExistAndSendPasswordResetToken(graphene.Mutation):
    """
        Accepts user's email and validates if email exist. If the email address exists, a validation email 
        is sent with the valid jwt token.
    """
    class Arguments: 
        email = graphene.String(required=True)

    token = graphene.String()
    success = graphene.Boolean()

    @classmethod
    def mutate(cls, unused_root, unused_info, email):
        del unused_root, unused_info

        try: 
            user = CustomUser.objects.get(email=email)
        except:
            return  ValidateEmailExistAndSendPasswordResetToken(success=False)

        token = get_token(user, "password_reset")

        # Returning token is just in case, main purpose is for sending to the user's email.

        return ValidateEmailExistAndSendPasswordResetToken(success=True, token=token)


class AuthMutations(ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    refresh_token = mutations.RefreshToken.Field()
    forgot_password = mutations.PasswordReset.Field()

class CustomAuthMutations(ObjectType):
    send_reset_password_email = ValidateEmailExistAndSendPasswordResetToken.Field()
