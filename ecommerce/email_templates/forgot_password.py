from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_forgot_password_email(receiver_email: str, sender_email: str, 
                            username: str, token: str, frontend_website: str) -> str:
    message = MIMEMultipart("alternative")
    message["Subject"] = "Reset Password"
    message["From"] = sender_email
    message["To"] = receiver_email
    reset_password_link = frontend_website + f"/change-password/{token}"

    text = f"""\
        Hi {username}, 
        Forgot your password? Click here to set up a new one. 
        Go here to set up a new one: {reset_password_link}/
    """

    html = f"""\
            <html>
                <head>
                    <style type="text/css">
                        #button{{
                            background-color: #1a202c;
                            padding: 1rem 1.5rem;
                            font-weight: bold;
                            border-radius: 8px;
                            width: fit-content;
                            margin: 0 auto;
                        }}
                        #link{{
                            text-decoration: none;
                        }}
                        a{{
                            color: white;
                        }}
                        body{{
                            display: grid;
                            place-items: center;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif
                        }}
                        #icon-container{{
                            width: fit-content;
                            margin: 0 auto;
                         }}
                    </style>
                </head>
                <body>
                    <div id="icon-container"><img src="https://res.cloudinary.com/dmmhsq8ti/image/upload/v1630310494/khong-icon_wzjx1g.png" /></div>
                    <h3>Hi, {username.capitalize()}<h3>
                    <p>Forgot your password? Click below to set up a new one.</p> 
                    <div id="button">
                        <a id="link" href={reset_password_link}>Reset Password</a>
                    </div>
                </body> 
            </html>
    """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    return message.as_string()
