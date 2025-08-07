import hmac
import base64
import hashlib
import urllib.parse
import logging

logger = logging.getLogger(__name__)

def gen_sig(sec_key: str, http_method: str, decode_api_path: str, token: str, ts_str: str) -> (str|None):
    # 生成data
    # 对decode_api_path进行处理
    while decode_api_path.endswith('/'):
        decode_api_path = decode_api_path[:-1]
    encode_api_path = urllib.parse.quote(decode_api_path, safe='')

    # 拼接data
    data = f"{http_method}&{encode_api_path}"
    if token:
        data += f"&{token}"
    data += f"&{ts_str}"

    # 使用HMAC-SHA1进行加密
    try:
        # 将key转换为字节
        key_bytes = sec_key.encode()
        # 将data转换为字节
        data_bytes = data.encode()

        # 使用HMAC-SHA1进行加密
        mac = hmac.new(key_bytes, data_bytes, hashlib.sha1)

        # 返回Base64编码的结果
        return base64.b64encode(mac.digest()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

