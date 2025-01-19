import os

from dotenv import load_dotenv
from requests import Session

from python_picnic_api.python_picnic_api import PicnicAPI
from python_picnic_api.python_picnic_api.session import PicnicAPISession, PicnicAuthError

load_dotenv()

username = os.getenv("PICNIC_USERNAME")
password = os.getenv("PICNIC_PASSWORD")
country_code = "DE"

DEFAULT_URL = "https://storefront-prod.{}.picnicinternational.com/api/{}"
DEFAULT_API_VERSION = "15"


def test_init() -> None:
    assert issubclass(PicnicAPISession, Session)


def test_login() -> None:
    picnic = PicnicAPI(username, password, country_code=country_code)
    assert "x-picnic-auth" in picnic.session.headers.keys()


def test_login_auth_error() -> None:
    try:
        _ = PicnicAPI("username", "password", country_code=country_code)
    except PicnicAuthError:
        assert True
    else:
        assert False
