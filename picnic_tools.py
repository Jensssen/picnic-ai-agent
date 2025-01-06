import os

from dotenv import load_dotenv

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
        }
    ]
}


def format_price(value):
    euros = value / 100
    return f"{euros:.2f} Euro"


def search_for_products(search_query: str) -> dict:
    """Search for products on the Picnic platform.

    Args:
        search_query: Product name that shall be searched.

    Returns:
        A list of products that are available on the Picnic platform, sorted by price.
    """
    max_item_return_count = 3
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
    return {"picnic_response": f"Successfully added product to shopping cart"}


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
    return {"picnic_response": f"Successfully removed product from shopping cart"}
