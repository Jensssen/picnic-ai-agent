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