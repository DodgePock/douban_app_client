def is_dict_proxy_available(proxy: dict) -> bool:
    if proxy is None:
        return False
    if not isinstance(proxy, dict):
        return False
    #key mode、host、port must be in proxy
    if not all(key in proxy for key in ['mode', 'host', 'port']):
        return False
    return True

def proxy_format_dict_to_url(proxy: dict) -> str:
    if not is_dict_proxy_available(proxy):
        return None
    mode, host, port = proxy['mode'], proxy['host'], proxy['port']
    if proxy.get('username') and proxy.get('password'):
        username, password = proxy['username'], proxy['password']
        return f"{mode}://{username}:{password}@{host}:{port}"
    return f"{mode}://{host}:{port}"