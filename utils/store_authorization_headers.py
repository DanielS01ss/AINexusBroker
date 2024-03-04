
authorization_token = ""

def store_authorization_token(auth_token):
    global authorization_token
    authorization_token = auth_token

def get_authorization_token():
    return authorization_token

