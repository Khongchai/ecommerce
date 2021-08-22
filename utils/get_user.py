def get_user_from_context(info):
    try:
            user = info.context["user"]
    except:
        try:
            user = info.context.user
        except:
            raise ValueError("Context not provided")

    return user