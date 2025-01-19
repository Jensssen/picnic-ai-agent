import json
import re
from typing import List, Generator

# prefix components:
space = "    "
branch = "│   "
# pointers:
tee = "├── "
last = "└── "

IMAGE_SIZES = ["small", "medium", "regular", "large", "extra-large"]
IMAGE_BASE_URL = "https://storefront-prod.nl.picnicinternational.com/static/images"

SOLE_ARTICLE_ID_PATTERN = re.compile(r'"sole_article_id":"(\w+)"')


def _tree_generator(response: list, prefix: str = "") -> Generator:
    """A recursive tree generator,
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    # response each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(response) - 1) + [last]
    for pointer, item in zip(pointers, response):
        if "name" in item:  # print the item
            pre = ""
            if "unit_quantity" in item.keys():
                pre = f"{item['unit_quantity']} "
            after = ""
            if "display_price" in item.keys():
                after = f" €{int(item['display_price']) / 100.0:.2f}"

            yield prefix + pointer + pre + item["name"] + after
        if "items" in item:  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from _tree_generator(item["items"], prefix=prefix + extension)


def _url_generator(url: str, country_code: str, api_version: str) -> str:
    return url.format(country_code.lower(), api_version)


def _get_category_id_from_link(category_link: str) -> str | None:
    pattern = r"categories/(\d+)"
    first_number = re.search(pattern, category_link)
    if first_number:
        result = str(first_number.group(1))
        return result
    else:
        return None


def _get_category_name(category_link: str, categories: List[dict] | None) -> str | None:
    category_id = _get_category_id_from_link(category_link)
    if category_id:
        category = next(
            (item for item in categories if item["id"] == category_id), None)
        if category:
            return category["name"]
        else:
            return None
    else:
        return None


def get_recipe_image(id: str, size: str = "regular") -> str:
    sizes = IMAGE_SIZES + ["1250x1250"]
    assert size in sizes, "size must be one of: " + ", ".join(sizes)
    return f"{IMAGE_BASE_URL}/recipes/{id}/{size}.png"


def get_image(id: str, size: str = "regular", suffix: str = "webp") -> str:
    assert (
        "tile" in size if suffix == "webp" else True
    ), "webp format only supports tile sizes"
    assert suffix in ["webp", "png"], "suffix must be webp or png"
    sizes = IMAGE_SIZES + [f"tile-{size}" for size in IMAGE_SIZES]

    assert size in sizes, "size must be one of: " + ", ".join(sizes)
    return f"{IMAGE_BASE_URL}/{id}/{size}.{suffix}"


def _extract_search_results(raw_results: dict, max_items: int = 10) -> dict:
    """Extract search results from the nested dictionary structure returned by Picnic search.
    Number of max items can be defined to reduce excessive nested search"""
    search_results = []

    def find_articles(node: dict) -> None:
        if len(search_results) >= max_items:
            return

        content = node.get("content", {})
        if content.get("type") == "SELLING_UNIT_TILE" and "sellingUnit" in content:
            selling_unit = content["sellingUnit"]
            sole_article_ids = SOLE_ARTICLE_ID_PATTERN.findall(json.dumps(node))
            sole_article_id = sole_article_ids[0] if sole_article_ids else None
            result_entry = {
                **selling_unit,
                "sole_article_id": sole_article_id,
            }
            search_results.append(result_entry)

        for child in node.get("children", []):
            find_articles(child)

    body = raw_results.get("body", {})
    find_articles(body.get("child", {}))

    return {"items": search_results}


def _extract_recipe_search_results(raw_results: dict, max_items: int = 10) -> dict:
    """Extract recipe search results from the nested dictionary structure returned by Picnic recipe search.
    Number of max items can be defined to reduce excessive nested search"""
    search_results = []

    def find_articles(node: dict) -> None:
        if len(search_results) >= max_items:
            return
        if "recipe-tile__" in node.get("id", ""):
            content = node.get("pml", {})
            component = content.get("component", {})
            recipe_name = component.get("accessibilityLabel", None)

            search_results.append({"recipe_name": recipe_name})

        for child in node.get("children", []):
            find_articles(child)

    body = raw_results.get("body", {})
    child = body.get("child", {})
    find_articles(child)
    analytics = child.get("analytics", {})
    contexts = analytics.get("contexts", [])
    if len(contexts) > 0:
        contexts = contexts[-1]
        data = contexts.get("data", {})
        recipe_ids = data.get("recipe_ids", [])
        if len(recipe_ids) >= max_items:
            for idx, search_result in enumerate(search_results):
                search_result["id"] = recipe_ids[idx]

    return {"items": search_results}


def _extract_recipe_ingredients(raw_results: dict) -> list[dict]:
    """Extract the ingredients of a recipe id from the nested dictionary structure returned by Picnic."""
    ingredients = []

    def find_articles(node: dict) -> None:
        if 'recipe-portioning-content-wrapper' in node.get("id", ""):
            child = node.get("child", {})
            state = child.get("state", {})
            ingredients.append(state.get('coreIngredientsState', []))

        for child in node.get("children", []):
            find_articles(child)

    body = raw_results.get("body", {})
    child = body.get("child", {})
    child = child.get("child", {})
    find_articles(child)
    return ingredients[0]
