# Picnic AI Agent

This project demonstrates an agentic use case for interacting with the online grocery store [Picnic](https://picnic.app/).
Picnic is a Dutch online supermarket that delivers groceries to your door. I am a big fan of their service and 
simply wanted to create a fun project that combines their API with AI, without using any big agent framework such as LangGraph or Swarm. 
As an ML model, I have chosen the latest version of Googles Gemini model series called [Gemini 2.0 Flash](https://ai.google.dev/gemini-api/docs/models/gemini#gemini-2.0-flash) which is currently
in experimental state. However, it is multimodal and accepts/generates not only written text but also voice out of the box. 

### Setup
**This project requires a Google Gemini API key and a Picnic account.**

1. Create a .env file in the root directory and add the necessary environment variables. You can use the .env.example file as a template.
2. Create a virtual environment using `uv venv` and activate it using `source .venv/bin/activate`.
3. Run `uv run python picnic_agent.py` to start the agent.

### How to run
In order to run the agent, simply execute `uv run python picnic_agent.py`. The agent will start and wait for your commands.
At this moment in time, it is necessary to use a headset, while talking to the agent, as it uses the microphone to 
listen to your commands. Otherwise, the agent would talk to himself. `picnic_agent.py` is running the Gemini API in "TEXT" mode. 
That means that the model response modality is text and not voice. In a second step, I am converting the text response to speech using the 
[Text-to-Speech API](https://cloud.google.com/text-to-speech?hl=en) from Google. This gives me a lot more flexibility in terms of 
language and voice selection. The downside of this approach is that I loose the speech interruption feature. 
I always have to wait until the AI has finished speaking. I also tested the AUDIO response mode. However, that mode still seams to 
be a bit buggy. It by fare does not perform as well as the Text mode, which might be, because of the experimental state of the model.

### Available Tools
The AI agent has access to the following tools:
- search_for_products: Search for products in the Picnic store.
- add_product_to_cart: Add a product to your shopping cart.
- remove_product_from_cart: Remove a product from your shopping cart.
- search_for_recipes: Search for recipes on Picnic.
- add_recipe_to_cart: Add a full recipe to your shopping cart.
- search_for_cheaper_product_alternative: Search for a cheaper product alternative.
- replace_existing_product: Replace an existing product in your shopping cart with an alternative one.
- get_all_current_products_in_cart: Get all products currently present in your shopping cart.

### Disclaimer
This project was a fun, private project of min and is not associated in any way with Picnic or any other company/person. 
Idea and implementation are my own and are not intended to be used in any commercial context. The API could have been a completely different one. 
I have chosen the Picnic API, simply because I am a big fan of their service.