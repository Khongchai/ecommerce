def get_authenticated_user(info):
    try:
            user = info.context["user"]
    except:
        try:
            user = info.context.user
        except:
            raise ValueError("Context not provided")

    return user