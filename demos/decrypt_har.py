# 用于解密米家APP抓包
# ref: https://imkero.net/posts/mihome-app-api/

import argparse
import base64
import hashlib
import json
import gzip
from io import BytesIO
from Crypto.Cipher import ARC4
from urllib.parse import parse_qs

def parse_args():
    parser = argparse.ArgumentParser(description='Decrypt Mi Home App API requests.')
    parser.add_argument('-p', '--har_path', required=True, help='Path to the HAR file.')
    return parser.parse_args()

def decrypt_rc4(password, payload):
    r = ARC4.new(base64.b64decode(password))
    r.encrypt(bytes(1024))
    rawPayload = base64.b64decode(payload)
    return r.encrypt(rawPayload)

def get_signed_nonce(ssecurity, nonce):
    hash_object = hashlib.sha256(base64.b64decode(ssecurity) + base64.b64decode(nonce))
    return base64.b64encode(hash_object.digest()).decode('utf-8')

def gzip_unzip(bytes):
    compressedFile = BytesIO()
    compressedFile.write(bytes)
    compressedFile.seek(0)
    return gzip.GzipFile(fileobj=compressedFile, mode='rb').read()

def decrypt(nonce, ssecurity, data, isGzipped = False):
    signed_nonce = get_signed_nonce(ssecurity, nonce)
    decrypted_data = decrypt_rc4(signed_nonce, data)
    if isGzipped:
        decrypted_data = gzip_unzip(decrypted_data)

    try:
        decrypted_data = decrypted_data.decode("utf-8")
    except UnicodeDecodeError:
        decrypted_data = gzip_unzip(decrypted_data).decode("utf-8")

    return decrypted_data

def decrypt_request(request):
    request_data = request.get('postData', {}).get('text', '')
    if not request_data:
        return None, None, None
    request_data = parse_qs(request_data)
    request_data = {k: v[0] for k, v in request_data.items() if isinstance(v, list) and len(v) == 1}
    nonce = request_data.get('_nonce')
    ssecurity = request_data.get('ssecurity')
    data = request_data.get('data')
    if not nonce or not ssecurity or not data:
        return None, nonce, ssecurity
    decrypted_data = decrypt(nonce, ssecurity, data)
    return decrypted_data, nonce, ssecurity

def decrypt_response(response, nonce, ssecurity):
    response_body = response.get('content', {}).get('text', '')
    if not response_body:
        return None
    response_headers = response.get('headers', [])
    is_gzipped = False
    for header in response_headers:
        if header['name'].lower() == 'miot-content-encoding' and header['value'].lower() == 'gzip':
            is_gzipped = True
            break
    if not nonce or not ssecurity:
        return None
    decrypted_response = decrypt(nonce, ssecurity, response_body, is_gzipped)
    return decrypted_response

def simplify_har(har_data):
    data = []
    for entry in har_data['log']['entries']:
        if entry.get('request', {}).get('method') != 'POST':
            continue
        request_url = entry.get('request', {}).get('url')
        request_method = entry.get('request', {}).get('method')
        request_data = entry.get('request', {}).get('postData', {})
        response_status = entry.get('response', {}).get('status')
        response_content = entry.get('response', {}).get('content', {})
        started_date = entry.get('startedDateTime')
        latency = entry.get('time', 0)

        data.append({
            'request': {
                'url': request_url,
                'method': request_method,
                'postData': request_data,
            },
            'response': {
                'status': response_status,
                'content': response_content,
            },
            'startedDateTime': started_date,
            'time': latency,
        })
    return data

if __name__ == "__main__":
    args = parse_args()
    with open(args.har_path, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    entries = []
    for entry in har_data['log']['entries']:
        request = entry['request']
        if request['method'] != 'POST':
            entries.append(entry)
            continue

        decrypted_data, nonce, ssecurity = decrypt_request(request)
        if decrypted_data:
            entry['request']['postData']['data'] = json.loads(decrypted_data)

        decrypted_response = decrypt_response(entry.get('response', {}), nonce, ssecurity)
        if decrypted_response:
            entry['response']['content']['data'] = json.loads(decrypted_response)
        entries.append(entry)
    har_data['log']['entries'] = entries
    save_name = args.har_path.rsplit('.', 1)[0] + '_decrypted.har'
    with open(save_name, 'w', encoding='utf-8') as f:
        json.dump(har_data, f, ensure_ascii=False, indent=2)
    print(f'Decrypted HAR file saved as: {save_name}')
    save_name = save_name.rsplit('.', 1)[0] + '_simplified.json'
    with open(save_name, 'w', encoding='utf-8') as f:
        json.dump(simplify_har(har_data), f, ensure_ascii=False, indent=2)
    print(f'Simplified HAR file saved as: {save_name}')
