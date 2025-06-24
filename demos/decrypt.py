# 用于解密米家APP抓包
# ref: https://imkero.net/posts/mihome-app-api/

import argparse
import base64
import hashlib
import gzip
from io import BytesIO
from Crypto.Cipher import ARC4

def parse_args():
    parser = argparse.ArgumentParser(description='Decrypt Mi Home App API requests.')
    parser.add_argument('--nonce', required=True, help='Nonce value from the request.')
    parser.add_argument('--ssecurity', required=True, help='Ssecurity value from the request.')
    # data 参数可以是请求体中 data 字段的值，也可以是响应体
    parser.add_argument('--data', required=True, help='Encrypted data from the request or response.')
    # 若解密的是响应 Body，且响应 Header 中有 miot-content-encoding: GZIP，需要设置为 True
    parser.add_argument('--is_gzipped', action='store_true', help='Indicates if the data is gzipped.')
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

if __name__ == "__main__":
    args = parse_args()
    nonce = args.nonce
    ssecurity = args.ssecurity
    data = args.data
    isGzipped = args.is_gzipped
    decrypted_data = decrypt_rc4(get_signed_nonce(ssecurity, nonce), data)
    if isGzipped:
        decrypted_data = gzip_unzip(decrypted_data)

    try:
        decrypted_data = decrypted_data.decode("utf-8")
    except UnicodeDecodeError:
        decrypted_data = gzip_unzip(decrypted_data).decode("utf-8")
    print(decrypted_data)
