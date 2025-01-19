import os
from typing import Dict

from dotenv import load_dotenv

from ai_helper_functions import find_product_in_cart
from python_picnic_api.python_picnic_api import PicnicAPI

load_dotenv()

picnic = PicnicAPI(username=os.environ.get("PICNIC_USERNAME"),
                   password=os.environ.get("PICNIC_PASSWORD"),
                   country_code=os.environ.get("PICNIC_REGION"))

tools = {
    "function_declarations": [
        {
            "name": "search_for_products",
            "description": "Searches for products on the online grocery platform Picnic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "search_query": {
                        "type": "STRING",
                        "description": "The name of the product that shall be searched such as milk or apples"
                    },
                    "max_item_return_count": {
                        "type": "NUMBER",
                        "description": "Number of returned products. Can be between 0 and 10."
                    }
                },
                "required": ["search_query"]
            }
        },
        {
            "name": "add_product_to_cart",
            "description": "Adds a product to the Picnic platform shopping cart.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "product_id": {
                        "type": "STRING",
                        "description": "The ID of the product that shall be added to the online picnic shopping cart."
                    },
                    "count": {
                        "type": "NUMBER",
                        "description": "The amount of products to add to the online picnic shopping cart. Default to 1."
                    }
                },
                "required": ["product_id"]
            }
        },
        {
            "name": "remove_product_from_cart",
            "description": "Removes a product from the Picnic platform shopping cart.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "product_id": {
                        "type": "STRING",
                        "description": "The ID of the product that shall be removed from the online picnic shopping "
                                       "cart."
                    },
                    "count": {
                        "type": "NUMBER",
                        "description": "The amount of products to remove from the online picnic shopping cart. Default "
                                       "to 1."
                    }
                },
                "required": ["product_id"]
            }
        },
        {
            "name": "search_for_recipes",
            "description": "Searches for recipes on the online grocery platform Picnic.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "search_query": {
                        "type": "STRING",
                        "description": "Name of the recipe that shall be searched such as pizza or spaghetti bolognese."
                    },
                    "max_item_return_count": {
                        "type": "NUMBER",
                        "description": "Number of returned recipes. Can be between 0 and 10."
                    }
                },
                "required": ["search_query"]
            }
        },
        {
            "name": "add_recipe_to_cart",
            "description": "Adds a recipe to the Picnic platform shopping cart.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "recipe_id": {
                        "type": "STRING",
                        "description": "The ID of the recipe that shall be added to the online picnic shopping cart."
                    }
                },
                "required": ["recipe_id"]
            }
        },
        {
            "name": "search_for_cheaper_product_alternative",
            "description": "Returns a list of product alternatives, sorted by its price, starting with the cheapest.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "product_name": {
                        "type": "STRING",
                        "description": "The name of the product that we want to search cheaper alternatives for."
                    }
                },
                "required": ["product_name"]
            }
        },
        {
            "name": "replace_existing_product",
            "description": "Replace an existing product in the users shopping cart with a new one.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "old_product_id": {
                        "type": "STRING",
                        "description": "Product id of the old product that shall be replaced."
                    },
                    "new_product_id": {
                        "type": "STRING",
                        "description": "Product id of the new product."
                    }
                },
                "required": ["old_product_id", "new_product_id"]
            }
        },
        {
            "name": "get_all_current_products_in_cart",
            "description": "Get a list of all products that are currently in the shopping cart.",
            "required": []
        },
    ]
}


def format_price(value: int) -> str:
    euros = value / 100
    return f"{euros:.2f} Euro"


def search_for_products(search_query: str, max_item_return_count: int = 3) -> dict:
    """Search for products on the Picnic platform.

    Args:
        search_query: Product name that shall be searched.
        max_item_return_count: Maximum number of returned products.

    Returns:
        A list of products that are available on the Picnic platform, sorted by price.
    """
    products = picnic.search(search_query)[0]["items"]
    filtered_products = []
    if len(products) > 0:
        products = sorted(products, key=lambda x: x['display_price'])
        for product in products[0:max_item_return_count]:
            filtered_products.append({
                "name": product['name'].replace(",", "."),
                "price": format_price(product['display_price']),
                "id": product['id']
            })
    else:
        return {
            "products": "No product could be found!"
        }
    return {
        "products": filtered_products
    }


def add_product_to_cart(product_id: str, count: int = 1) -> dict:
    """Adds a product to your online shopping cart.

    Args:
        product_id: ID of the product that shall be added.
        count: Number of products to add to shopping cart.

    Returns:
        The name of the product that was added.
    """
    product_id = product_id.lower().strip()
    response = picnic.add_product(product_id, count=count)
    if response["error"]:
        return {"picnic_response": response["error"]["code"]}
    for item in response["items"]:
        if item["items"][0]["id"] == product_id:
            item_name = item["items"][0]["name"]
            return {"picnic_response": f"Successfully added {item_name} to shopping cart"}
    return {"picnic_response": "Successfully added product to shopping cart"}


def remove_product_from_cart(product_id: str, count: int = 1) -> dict:
    """Removes a product from the shopping cart.

    Args:
        product_id: ID of the product that shall be removed.
        count: Number of products to remove from the shopping cart.

    Returns:
        The name of the product that was removed.
    """
    product_id = product_id.lower().strip()
    response = picnic.remove_product(product_id, count=count)
    if response["error"]:
        return {"picnic_response": response["error"]["code"]}
    for item in response["items"]:
        if item["items"][0]["id"] == product_id:
            item_name = item["items"][0]["name"]
            return {"picnic_response": f"Successfully removed {item_name} from shopping cart"}
    return {"picnic_response": "Successfully removed product from shopping cart"}


def search_for_recipes(search_query: str, max_item_return_count: int = 3) -> dict:
    """Search for recipes on the Picnic platform.

    Args:
        search_query: Recipe that shall be searched.
        max_item_return_count: Maximum number of returned recipes.

    Returns:
        A list of recipes that are available on the Picnic platform, sortd by relevance.
    """
    recipes = picnic.search_recipe(search_query)[0]["items"]
    if len(recipes) == 0:
        return {
            "recipes": "No recipes could be found!"
        }
    return {
        "recipes": recipes[0:max_item_return_count]
    }


def add_recipe_to_cart(recipe_id: str) -> Dict[str, str]:
    """Adds a recipe to your online shopping cart.

    Args:
        recipe_id: ID of the recipe that shall be added.

    Returns:
        The name of the recipe that was added.
    """
    recipe_id = recipe_id.lower().strip()
    response = picnic.add_recipe_to_cart(recipe_id)
    if response["error"]:
        return {"picnic_response": response["error"]["code"]}
    return {"picnic_response": "Successfully added the recipe to your shopping cart"}


def search_for_cheaper_product_alternative(product_name: str) -> dict:
    """
    Search for a cheaper alternative product on the Picnic platform.

    Args:
        product_name: Name of the product that shall be replaced.
    """
    MAX_PRODUCTS_TO_RETURN = 6
    current_cart = picnic.get_cart()
    cart_items = current_cart.get("items", [])
    filtered_cart_items = [
        {"price": item["display_price"], "product_name": item["items"][0]["name"], "product_id": item["items"][0]["id"]}
        for item in cart_items]
    product_to_replace = find_product_in_cart(filtered_cart_items, product_name)
    products = picnic.search(product_to_replace.short_product_name_version)[0]["items"]
    filtered_products = [
        {"price": product["display_price"], "product_name": product["name"], "product_id": product["id"]} for product in
        products[0:MAX_PRODUCTS_TO_RETURN]]
    sorted_products = sorted(filtered_products, key=lambda x: x['price'])
    return {"picnic_response": sorted_products}


def replace_existing_product(old_product_id: str, new_product_id: str) -> dict:
    """
    Replace an existing product in the users shopping cart with a new one.

    Args:
        old_product_id: Product id of the old product that shall be replaced.
        new_product_id: Product id of the new product.
    """
    response = picnic.remove_product(product_id=old_product_id)
    if response["error"]:
        return {"picnic_response": response["error"]["code"]}
    response = picnic.add_product(product_id=new_product_id)
    if response["error"]:
        return {"picnic_response": response["error"]["code"]}
    return {"picnic_response": "Successfully replaced the product in your shopping cart."}


def get_all_current_products_in_cart() -> dict:
    """Get all products that are currently in the shopping cart.    """
    current_cart = picnic.get_cart()
    cart_items = current_cart.get("items", {})
    filtered_cart_items = [
        {"price": item["display_price"], "product_name": item["items"][0]["name"], "product_id": item["items"][0]["id"]}
        for item in cart_items]
    return {"picnic_response": filtered_cart_items}
