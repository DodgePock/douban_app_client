from douban_app_client import DoubanAppClient
from config import client_init
import logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO
)

client = DoubanAppClient(**client_init)

resp = client.RESTful_request('GET', 'https://frodo.douban.com/api/v2/user/1000001')
if resp['code'] == 0:
    logger.info(f"{resp['data']['name']}")
else:
    logger.error(f"Failed to fetch user info: {resp['msg']} (code: {resp['code']})")