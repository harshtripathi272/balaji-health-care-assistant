import os
from firebase_config.config import db
from Data.orders import add_orders, get_orders, update_orders
from Data.chatbot_log import add_chatbot_log, delete_chatbot_log, get_chatbot_log_by_id, get_chatbot_logs
from Data.clients import add_client, delete_client, get_client_by_id, get_clients, update_client
from Data.inventory import add_inventory, delete_inventory, get_inventory, get_inventory_by_id, update_inventory
from Data.suppliers import add_supplier, delete_supplier, get_supplier_by_id, get_suppliers, update_supplier

from google.generativeai import configure, GenerativeModel
from dotenv import load_dotenv


load_dotenv()
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("gemini-2.0-flash")

FEW_SHOT_PROMPT = """
You are a business assistant. Convert user requests into internal function calls.

Examples:
User: Show me all inventory items
Action: get_inventory()

User: Add 10 syringes to inventory for CHL
Action: add_inventory(inventory_data={{"item": "syringe", "quantity": 10, "client": "CHL"}})

User: Update inventory item with ID 'abc123' to have quantity 50
Action: update_inventory(inventory_id="abc123", updated_data={{"quantity": 50}})

User: Delete inventory item with ID 'xyz789'
Action: delete_inventory(inventory_id="xyz789")

User: Show details of inventory item with ID 'inv456'
Action: get_inventory_by_id(inventory_id="inv456")

Now convert the user query below to an action.
User: {user_input}
"""




def parse_action(user_input):
    prompt = FEW_SHOT_PROMPT.format(user_input=user_input)
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Remove "Action: " prefix if it exists
    if response_text.lower().startswith("action:"):
        return response_text[len("Action:"):].strip()
    return response_text



def execute_action(action_str):
    try:
        result = eval(action_str)
        return result if result else "Action executed successfully."
    except Exception as e:
        return f"Error executing action: {e}"
    
def handle_user_input(user_input):
    action = parse_action(user_input)
    print("Gemini Suggested action ",action)
    return execute_action(action)


