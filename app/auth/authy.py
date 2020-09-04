import time
import qrcode
import jwt as pyjwt
import qrcode.image.svg
from io import BytesIO
from flask import current_app, request
from authy.api import AuthyApiClient


def get_registration_jwt(user_id, expires_in=5 * 60):
    now = time.time()
    payload = {
     'iss': current_app.config['AUTHY_APP_NAME'],
     'iat': now,
     'exp': now + expires_in,
     'context': {
         'custom_user_id': str(user_id),
         'authy_app_id': current_app.config['AUTHY_APP_ID'],
     }
    }
    return pyjwt.encode(payload, current_app.config['AUTHY_PRODUCTION_API_KEY']).decode()


def get_qrcode(jwt):
    qr = qrcode.make('authy://account?token=' + jwt, image_factory=qrcode.image.svg.SvgImage)
    stream = BytesIO()
    qr.save(stream)
    return stream.getvalue()


def get_registration_status(user_id):
    authy_api = AuthyApiClient(current_app.config['AUTHY_PRODUCTION_API_KEY'])
    resp = authy_api.users.registration_status(user_id)
    if not resp.ok():
        return {'status': 'pending'}
    return resp.content['registration']


def validate_token_auth(user, token):
    authy_api = AuthyApiClient(current_app.config['AUTHY_PRODUCTION_API_KEY'])
    validation = authy_api.tokens.verify(user.authy_id, token)
    return validation.ok()


def delete_user(authy_id):
    authy_api = AuthyApiClient(current_app.config['AUTHY_PRODUCTION_API_KEY'])
    resp = authy_api.users.delete(authy_id)
    return resp.ok()
