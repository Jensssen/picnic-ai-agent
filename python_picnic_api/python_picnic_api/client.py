from hashlib import md5
from typing import List, Dict

from .helper import _tree_generator, _url_generator, _get_category_name, _extract_search_results, \
    _extract_recipe_search_results, _extract_recipe_ingredients
from .session import PicnicAPISession, PicnicAuthError
from requests import Response

DEFAULT_URL = "https://storefront-prod.{}.picnicinternational.com/api/{}"
DEFAULT_COUNTRY_CODE = "DE"
DEFAULT_API_VERSION = "15"


class PicnicAPI:
    def __init__(
            self, username: str | None = None, password: str | None = None,
            country_code: str | None = DEFAULT_COUNTRY_CODE, auth_token: str | None = None
    ):
        self._country_code = country_code
        self._base_url = _url_generator(
            DEFAULT_URL, self._country_code, DEFAULT_API_VERSION
        )

        self.session = PicnicAPISession(auth_token=auth_token)

        # Login if not authenticated
        if not self.session.authenticated and username and password:
            self.login(username, password)

        self.high_level_categories: List[dict] | None = None

    def initialize_high_level_categories(self) -> None:
        """Initialize high-level categories once to avoid multiple requests."""
        if not self.high_level_categories:
            self.high_level_categories = self.get_categories(depth=1)

    def _get(self, path: str, add_picnic_headers: bool = False) -> dict:
        url = self._base_url + path

        # Make the request, add special picnic headers if needed
        headers = {
            "x-picnic-agent": "30100;1.15.269-#15289;",
            "x-picnic-did": "543809EC162F0B0B"
        } if add_picnic_headers else None
        response = self.session.get(url, headers=headers).json()

        if self._contains_auth_error(response):
            raise PicnicAuthError("Picnic authentication error")

        return response

    def _post(self, path: str, data: dict | None = None, add_picnic_headers: bool = False) -> Response:
        url = self._base_url + path

        # Make the request, add special picnic headers if needed
        headers = {
            "x-picnic-agent": "30100;1.15.269-#15289;",
            "x-picnic-did": "543809EC162F0B0B"
        } if add_picnic_headers else None
        response = self.session.post(url, json=data, headers=headers).json()

        if self._contains_auth_error(response):
            raise PicnicAuthError(f"Picnic authentication error: {response['error'].get('message')}")

        return response

    @staticmethod
    def _contains_auth_error(response: dict) -> bool:
        if not isinstance(response, dict):
            return False

        error_code = response.setdefault("error", {}).get("code")
        return error_code == "AUTH_ERROR" or error_code == "AUTH_INVALID_CRED"

    def login(self, username: str, password: str) -> Response:
        path = "/user/login"
        secret = md5(password.encode("utf-8")).hexdigest()
        data = {"key": username, "secret": secret, "client_id": 30100}

        return self._post(path, data)

    def logged_in(self) -> bool:
        return self.session.authenticated

    def get_user(self) -> dict:
        return self._get("/user")

    def search(self, term: str) -> List[Dict]:
        path = f"/pages/search-page-results?search_term={term}"
        raw_results = self._get(path, add_picnic_headers=True)
        search_results = _extract_search_results(raw_results)
        return [search_results]

    def search_recipe(self, term: str) -> List[Dict]:
        path = f"/pages/search-page-results?search_term={term}&is_recipe=true&selected_sorting=RELEVANCE"
        raw_results = self._get(path, add_picnic_headers=True)
        search_results = _extract_recipe_search_results(raw_results)
        return [search_results]

    def add_recipe_to_cart(self, recipe_id: str = "665d879b27b9fb2099389e95") -> Response:
        path = f"/pages/recipe-details-page?recipe_id={recipe_id}"
        raw_results = self._get(path, add_picnic_headers=True)
        body = raw_results.get("body", {})
        child = body.get("child", {})
        state = child.get("state", {})
        portions = state.get("servingsState", 1)

        core_ingredients = _extract_recipe_ingredients(raw_results)
        path = "/pages/task/assign-recipe-to-day"
        payload = {"payload": {"recipe_id": recipe_id, "portions": portions, "day_offset": None,
                               "core_ingredients": core_ingredients}}
        return self._post(path, payload, True)

    def get_lists(self, list_id: str | None = None) -> dict:
        if list_id:
            path = "/lists/" + list_id
        else:
            path = "/lists"
        return self._get(path)

    def get_sublist(self, list_id: str, sublist_id: str) -> dict:
        """Get sublist.

        Args:
            list_id (str): ID of list, corresponding to requested sublist.
            sublist_id (str): ID of sublist.

        Returns:
            list: Sublist result.
        """
        return self._get(f"/lists/{list_id}?sublist={sublist_id}")

    def get_cart(self) -> dict:
        return self._get("/cart")

    def get_article(self, article_id: str, add_category_name: bool = False) -> dict:
        path = "/articles/" + article_id
        article = self._get(path)
        if add_category_name and "category_link" in article:
            self.initialize_high_level_categories()
            article.update(
                category_name=_get_category_name(article['category_link'], self.high_level_categories)
            )
        return article

    def get_article_category(self, article_id: str) -> dict:
        path = "/articles/" + article_id + "/category"
        return self._get(path)

    def add_product(self, product_id: str, count: int = 1) -> Response:
        data = {"product_id": product_id, "count": count}
        return self._post("/cart/add_product", data)

    def remove_product(self, product_id: str, count: int = 1) -> Response:
        data = {"product_id": product_id, "count": count}
        return self._post("/cart/remove_product", data)

    def clear_cart(self) -> Response:
        return self._post("/cart/clear")

    def get_categories(self, depth: int = 0) -> List[Dict]:
        return self._get(f"/my_store?depth={depth}")["catalog"]

    def print_categories(self, depth: int = 0) -> None:
        tree = "\n".join(_tree_generator(self.get_categories(depth=depth)))
        print(tree)


__all__ = ["PicnicAPI"]
