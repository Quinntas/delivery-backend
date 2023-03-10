from datetime import datetime, timedelta

import jwt.exceptions
from decouple import config
from jwt import JWT, jwk_from_dict
from jwt.utils import get_int_from_datetime

JWT_SECRET = config('JWT_SECRET')
JWT_ALGORITHM = config('JWT_ALGORITHM')

jwt_instance = JWT()

_jwk = jwk_from_dict({
    'kty': 'oct',
    'alg': JWT_ALGORITHM,
    'k': JWT_SECRET,
})


class JWTResponse:
    def __init__(self, is_expired: bool, payload: dict = None):
        self.is_expired = is_expired
        self.payload = payload


def token_response(token_payload: str) -> dict:
    return {
        "token": token_payload
    }


def sign_jwt(payload: dict, exp_time: int = 6) -> dict:
    token_payload = {
        "payload": payload,
        "iat": get_int_from_datetime(datetime.utcnow()),
        "exp": get_int_from_datetime(datetime.utcnow() + timedelta(hours=exp_time))
    }
    token = jwt_instance.encode(payload=token_payload, key=_jwk, alg=JWT_ALGORITHM)
    return token_response(token)


def decode_jwt(token_payload: str) -> JWTResponse | None:
    try:
        decode_token = jwt_instance.decode(message=token_payload, key=_jwk, do_time_check=True, do_verify=True)
        if decode_token['exp'] < get_int_from_datetime(datetime.utcnow()):
            return JWTResponse(is_expired=True)
        return JWTResponse(is_expired=False, payload=decode_token['payload'])
    except jwt.exceptions.JWTDecodeError:
        return None
