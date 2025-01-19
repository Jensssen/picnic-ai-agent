import os
from typing import Any, Coroutine, List

import google.generativeai as genai
import instructor
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
client = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="models/gemini-1.5-flash-latest",
    ),
    mode=instructor.Mode.GEMINI_JSON,

)


class Product(BaseModel):
    price: int
    product_id: str
    product_name: str
    short_product_name_version: str


class AlternativeProduct(BaseModel):
    price: int
    product_id: str
    product_name: str


def find_product_in_cart(cart: List[dict], product_name: str) -> Coroutine[Any, Any, Product | Any]:
    """Searches for a specific product in a list of products by its name."""

    resp = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Here is a list of products: \n {cart} \n"
                           f"Find the product that matches the following search term: {product_name}",
            }
        ],
        response_model=Product,
    )
    return resp


def find_cheapest_alternative(cart: dict, product_name: str) -> Coroutine[Any, Any, AlternativeProduct | Any]:
    """Find a cheap alternative product in a list of products by name."""

    resp = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Here is a list of products: \n {cart} \nFind the product that is the cheapest of all and "
                           f"that fit to the following product name: {product_name} \n"
                           f"Low product price is very important!",
            }
        ],
        response_model=AlternativeProduct,
    )
    return resp
