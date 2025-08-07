import logging
import requests
from functools import partial
import time
from . import tools
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DoubanAppClient:
    def __init__(
        self,
        token: str,
        sec_key: str,
        user_agent: str,
        proxy_url: str = "http://blackhole.webpagetest.org",
        default_request_timeout: int = 10,
        default_exception_retry: int = 3,
        **kwargs,
    ):
        logger.info(f"{'*'*20} Bilibili Client init {'*'*20}")
        self.token = token
        self.sec_key = sec_key
        self.init_proxies(proxy_url, **kwargs)

        self.default_headers = {
            'Authorization': f'Bearer {token}',
            'Host': 'frodo.douban.com',
            'User-Agent': user_agent
        }

        self.init_session()

        self.default_request_timeout = default_request_timeout
        self.default_request_exception_retry = default_exception_retry

    def init_session(self):
        self.session = requests.Session()
        if self.proxies:
            self.session.proxies = self.proxies
        self.session.trust_env = False

        # 设置headers
        self.session.headers.update(self.default_headers)
    

    def init_proxies(self, proxy_url:str, **kwargs):
        # 初始化代理, 优先级：kwargs['proxy'] > proxy_url > proxy_url(default)
        # 如不使用代理，则需要同时设置proxy_url和kwargs['proxy']为None
        proxy = kwargs.get("proxy", None)
        proxy_url = (
            tools.proxy.proxy_format_dict_to_url(proxy)
            if tools.proxy.is_dict_proxy_available(proxy)
            else proxy_url
        )
        if proxy_url is None:
            logger.info("No proxy is set.")
            self.proxies = None

        # 若使用socks5代理，则替换成socks5h
        if proxy_url and proxy_url.startswith("socks5://"):
            proxy_url = proxy_url.replace("socks5://", "socks5h://")
        
        logger.info(f"Using proxy: {proxy_url}")
        self.proxies = {"http": proxy_url, "https": proxy_url}

    def RESTful_request(self, method:str, url:str, exception_retry:int=-1, **kwargs)->dict:
        kwargs['timeout'] = kwargs.get('timeout', self.default_request_timeout)
        exception_retry = exception_retry if exception_retry>=1 else self.default_request_exception_retry

        # 生成签名
        ts_str = str(int(time.time()))
        url_path = urlparse(url).path
        _sig = tools.api_signature_helper.gen_sig(self.sec_key, method, url_path, self.token, ts_str)
        kwargs['params'] = kwargs.get('params', {})
        kwargs['params']['_sig'] = _sig
        kwargs['params']['_ts'] = ts_str

        try:
            response = partial(self.session.request, method)(url, **kwargs)
            if response.status_code == 200:
                logger.info(f"{method} request success for url: {url}")
                data = response.json()
                return {'code': 0, 'data': data}
            else:
                warning_msg = f"{method} request failed for url: {url}, status code: {response.status_code}, response: {response.text}"
                logger.warning(warning_msg)
                return {'code': -100000000, 'message': warning_msg}
        except Exception as e:
            error_msg = f"{method} request failed for url: {url}, error: {e}"
            logger.error(error_msg)
            if exception_retry >= 1:
                exception_retry -= 1
                return self.RESTful_request(method, url, exception_retry, **kwargs)
            else:
                return {'code': -100000001, 'message': error_msg}
            



