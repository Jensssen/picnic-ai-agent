import os

from dotenv import load_dotenv

from python_picnic_api.python_picnic_api import PicnicAPI

load_dotenv()

username = os.getenv("PICNIC_USERNAME")
password = os.getenv("PICNIC_PASSWORD")
country_code = "DE"

picnic = PicnicAPI(username, password, country_code=country_code)


def _get_amount(cart: dict, product_id: str) -> int:
    items = cart["items"][0]["items"]
    product = next((item for item in items if item["id"] == product_id), None)
    return product["decorators"][0]["quantity"]


def test_get_user() -> None:
    response = picnic.get_user()
    assert isinstance(response, dict)
    assert "contact_email" in response.keys()
    assert response["contact_email"] == username


def test_search() -> None:
    response = picnic.search("Jacobs Krönung Klassisch gemahlen")
    assert isinstance(response, list)
    assert isinstance(response[0], dict)
    assert "id" in response[0]["items"][0].keys()
    assert response[0]["items"][0]["id"] == 's1020400'


def test_get_lists() -> None:
    response_1 = picnic.get_lists()
    response_2 = picnic.get_lists("19356")
    assert isinstance(response_1, list)
    assert isinstance(response_2, list)


def test_get_cart() -> None:
    response = picnic.get_cart()
    assert isinstance(response, dict)
    assert "id" in response.keys()
    assert response["id"] == "shopping_cart"


def test_add_product() -> None:
    # need a clear cart for reproducibility
    picnic.clear_cart()
    response = picnic.add_product("s1020400", count=2)

    assert isinstance(response, dict)
    assert "items" in response.keys()
    assert any(item["id"] == "s1020400" for item in response["items"][0]["items"])
    assert _get_amount(response, "s1020400") == 2
    picnic.clear_cart()


def test_remove_product() -> None:
    # need a clear cart for reproducibility
    picnic.clear_cart()
    # add two coffee to the cart, so we can remove 1
    picnic.add_product("s1020400", count=2)

    response = picnic.remove_product("s1020400", count=1)
    amount = _get_amount(response, "s1020400")

    assert isinstance(response, dict)
    assert "items" in response.keys()
    assert amount == 1
    picnic.clear_cart()


def test_clear_cart() -> None:
    # need a clear cart for reproducibility
    picnic.clear_cart()
    # add two coffee to the cart, so we can clear it
    picnic.add_product("s1020400", count=2)

    response = picnic.clear_cart()

    assert isinstance(response, dict)
    assert "items" in response.keys()
    assert len(response["items"]) == 0


def test_get_categories() -> None:
    response = picnic.get_categories()
    assert isinstance(response, list)
