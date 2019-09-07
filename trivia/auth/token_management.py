from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication, JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken


# verifies a JWTToken and returns the id of the verified user.
def validate_JWTToken(token):
	
	access_token = token
	token_obj = AccessToken(access_token)
	token_user = JWTTokenUserAuthentication().get_user(token_obj)

	return token_user.id