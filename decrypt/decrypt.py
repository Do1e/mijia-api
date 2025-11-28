import argparse
import json

from mijiaAPI import decrypt


def parse_args():
    parser = argparse.ArgumentParser(description="解密米家APP中的请求与响应数据")
    parser.add_argument("--ssecurity", required=True, help="请求数据中的 ssecurity 值")
    parser.add_argument("--nonce", required=True, help="请求数据中的 _nonce 值")
    parser.add_argument("--data", required=True, help="请求或响应中的加密数据")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    data = decrypt(args.ssecurity, args.nonce, args.data)
    data = json.loads(data)
    print(json.dumps(data, ensure_ascii=False))
