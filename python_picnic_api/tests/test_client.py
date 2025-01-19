import unittest
from unittest.mock import patch

from python_picnic_api.python_picnic_api import PicnicAPI
from python_picnic_api.python_picnic_api.client import DEFAULT_URL
from python_picnic_api.python_picnic_api.session import PicnicAuthError

PICNIC_HEADERS = {
    "x-picnic-agent": "30100;1.15.269-#15289;",
    "x-picnic-did": "543809EC162F0B0B"
}


class TestClient(unittest.TestCase):
    class MockResponse:
        def __init__(self, json_data: dict, status_code: int) -> None:
            self.json_data = json_data
            self.status_code = status_code

        def json(self) -> dict:
            return self.json_data

    def setUp(self) -> None:
        self.session_patcher = patch("python_picnic_api.client.PicnicAPISession")
        self.session_mock = self.session_patcher.start()
        self.client = PicnicAPI(username="test@test.nl", password="test")
        self.expected_base_url = DEFAULT_URL.format("nl", "15")

    def tearDown(self) -> None:
        self.session_patcher.stop()

    def test_login_credentials(self) -> None:
        self.session_mock().authenticated = False
        PicnicAPI(username='test@test.nl', password='test')
        self.session_mock().post.assert_called_with(
            self.expected_base_url + '/user/login',
            json={'key': 'test@test.nl', 'secret': '098f6bcd4621d373cade4e832627b4f6', "client_id": 1}
        )

    def test_login_auth_token(self) -> None:
        self.session_mock().authenticated = True
        PicnicAPI(username='test@test.nl', password='test', auth_token='a3fwo7f3h78kf3was7h8f3ahf3ah78f3')
        self.session_mock().login.assert_not_called()

    def test_login_failed(self) -> None:
        response = {
            "error": {
                "code": "AUTH_INVALID_CRED",
                "message": "Invalid credentials."
            }
        }
        self.session_mock().post.return_value = self.MockResponse(response, 200)

        client = PicnicAPI()
        with self.assertRaises(PicnicAuthError):
            client.login('test-user', 'test-password')

    def test_get_user(self) -> None:
        response = {
            "user_id": "594-241-3623",
            "firstname": "Firstname",
            "lastname": "Lastname",
            "address": {
                "house_number": 25,
                "house_number_ext": "b",
                "postcode": "1234 AB",
                "street": "Dorpsstraat",
                "city": "Het dorp",
            },
            "phone": "+31123456798",
            "contact_email": "test@test.nl",
            "total_deliveries": 25,
            "completed_deliveries": 20,
        }
        self.session_mock().get.return_value = self.MockResponse(response, 200)

        user = self.client.get_user()
        self.session_mock().get.assert_called_with(
            self.expected_base_url + "/user", headers=None
        )
        self.assertDictEqual(user, response)

    def test_search(self) -> None:
        self.client.search("test-product")
        self.session_mock().get.assert_called_with(
            self.expected_base_url + "/search?search_term=test-product", headers=None
        )

    def test_get_lists(self) -> None:
        self.client.get_lists()
        self.session_mock().get.assert_called_with(
            self.expected_base_url + "/lists", headers=None
        )

    def test_get_sublist(self) -> None:
        self.client.get_sublist(list_id="promotion", sublist_id="12345")
        self.session_mock().get.assert_called_with(
            self.expected_base_url + "/lists/promotion?sublist=12345", headers=None
        )

    def test_get_list_by_id(self) -> None:
        self.client.get_lists("abc")
        self.session_mock().get.assert_called_with(
            self.expected_base_url + "/lists/abc", headers=None
        )

    def test_get_cart(self) -> None:
        self.client.get_cart()
        self.session_mock().get.assert_called_with(
            self.expected_base_url + "/cart", headers=None
        )

    def test_add_product(self) -> None:
        self.client.add_product("p3f2qa")
        self.session_mock().post.assert_called_with(
            self.expected_base_url + "/cart/add_product",
            json={"product_id": "p3f2qa", "count": 1},
        )

    def test_add_multiple_products(self) -> None:
        self.client.add_product("gs4puhf3a", count=5)
        self.session_mock().post.assert_called_with(
            self.expected_base_url + "/cart/add_product",
            json={"product_id": "gs4puhf3a", "count": 5},
        )

    def test_remove_product(self) -> None:
        self.client.remove_product("gs4puhf3a", count=5)
        self.session_mock().post.assert_called_with(
            self.expected_base_url + "/cart/remove_product",
            json={"product_id": "gs4puhf3a", "count": 5},
        )

    def test_clear_cart(self) -> None:
        self.client.clear_cart()
        self.session_mock().post.assert_called_with(
            self.expected_base_url + "/cart/clear", json=None
        )

    def test_get_categories(self) -> None:
        self.session_mock().get.return_value = self.MockResponse(
            {
                "type": "MY_STORE",
                "catalog": [
                    {"type": "CATEGORY", "id": "purchases", "name": "Besteld"},
                    {"type": "CATEGORY", "id": "promotions", "name": "Acties"},
                ],
                "user": {},
            },
            200,
        )

        categories = self.client.get_categories()
        self.session_mock().get.assert_called_with(
            self.expected_base_url + "/my_store?depth=0", headers=None
        )

        self.assertDictEqual(
            categories[0], {"type": "CATEGORY", "id": "purchases", "name": "Besteld"}
        )

    def test_get_auth_exception(self) -> None:
        self.session_mock().get.return_value = self.MockResponse(
            {"error": {"code": "AUTH_ERROR"}}, 400
        )

        with self.assertRaises(PicnicAuthError):
            self.client.get_user()

    def test_post_auth_exception(self) -> None:
        self.session_mock().post.return_value = self.MockResponse(
            {"error": {"code": "AUTH_ERROR"}}, 400
        )

        with self.assertRaises(PicnicAuthError):
            self.client.clear_cart()
