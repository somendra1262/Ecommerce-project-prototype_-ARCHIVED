import base64, json, hmac, hashlib
from datetime import datetime, timezone

SECRET_KEY = b"your-secure-key"


def utf8bytes_to_base64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def pad_and_decode_to_original_bytes(data: str) -> bytes:
    rem = len(data) % 4
    if rem > 0: data += '=' * (4 - rem)
    return base64.urlsafe_b64decode(data)

def create_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}

    signing_input = utf8bytes_to_base64(json.dumps(header).encode('utf-8'))+"."+utf8bytes_to_base64(json.dumps(payload).encode('utf-8'))

    signature = hmac.new(SECRET_KEY, signing_input.encode('utf-8'), hashlib.sha256).digest()

    token=signing_input+"."+utf8bytes_to_base64(signature)
    return token


def verify_jwt(token: str) -> dict:
    recieved_header, recieved_payload, recieved_signature = token.split('.')
    signing_input = recieved_header+"."+recieved_payload


    expected_sig = hmac.new(SECRET_KEY, signing_input.encode('utf-8'), hashlib.sha256).digest()
    if not hmac.compare_digest(expected_sig, pad_and_decode_to_original_bytes(recieved_signature)):
        raise ValueError("Invalid Signature")

    payload = json.loads(pad_and_decode_to_original_bytes(recieved_payload).decode('utf-8'))

    # Check expiration
    if datetime.now(timezone.utc).timestamp() > payload["exp"]:
        raise ValueError("Token expired")
    return payload
