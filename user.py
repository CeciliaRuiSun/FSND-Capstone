from auth0.v3.authentication import Database

from auth import AUTH0_DOMAIN, AUTH0_CLIENT_ID

database = Database(AUTH0_DOMAIN)

def auth0_create_user(email, password):
    resp = database.signup(client_id=AUTH0_CLIENT_ID,
                           email=email,
                           password=password,
                           connection='Username-Password-Authentication')
    if "_id" in resp:
        return {
            "auth0_user_id" : "auth0|" + resp.get("_id"),
            "auth0_email" : resp.get("email")
        }
    else:
        raise("Failed to create user on auth0, resp: " + resp)
