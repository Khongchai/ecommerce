from ecommerce.email_templates.forgot_password import get_forgot_password_email
import smtplib
import ssl
from ecommerce.settings import env


import graphene
from graphene import ObjectType
from graphql_auth import mutations
from graphql_auth.utils import get_token
from users.models import CustomUser


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

        sender_email = env("SENDER_EMAIL")
        password = env("SENDER_PASSWORD")
        receiver_email = email
        port = 587
        message = get_forgot_password_email(receiver_email, sender_email, user.username, token, "http://localhost:3000")
        smtp_server = "smtp.gmail.com"

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)

        # Returning token is just in case, main purpose is for sending to the user's email.
        return ValidateEmailExistAndSendPasswordResetToken(success=True, token=token)


class AuthMutations(ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
    update_account = mutations.UpdateAccount.Field()
    refresh_token = mutations.RefreshToken.Field()
    reset_password = mutations.PasswordReset.Field()

class CustomAuthMutations(ObjectType):
    send_reset_password_email = ValidateEmailExistAndSendPasswordResetToken.Field()
