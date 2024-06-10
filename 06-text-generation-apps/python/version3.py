import os
from openai import AzureOpenAI
import json
import dotenv


# Load environment variables
dotenv.load_dotenv()

# Configure Azure OpenAI service client 
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2024-03-01-preview"
)


# Sample purchase orders data
purchase_orders = {
    "PON123": [
        {"line": 1, "description": "Item A", "quantity": 10, "unit_price": 5.0},
        {"line": 2, "description": "Item B", "quantity": 20, "unit_price": 7.5},
    ],
    "PON456": [
        {"line": 11, "description": "Item C", "quantity": 90, "unit_price": 11.0},
        {"line": 20, "description": "Item D", "quantity": 22, "unit_price": 5.5},
        {"line": 3, "description": "Item E", "quantity": 8, "unit_price": 4.4},
    ],
    "PON789": [
        {"line": 17, "description": "Item F", "quantity": 5, "unit_price": 8.0},
        {"line": 24, "description": "Item G", "quantity": 78, "unit_price": 6.5},
        {"line": 31, "description": "Item H", "quantity": 62, "unit_price": 7.3},
        {"line": 40, "description": "Item I", "quantity": 23, "unit_price": 9.8},
    ],
    "PON768": [
        {"line": 19, "description": "Item J", "quantity": 33, "unit_price": 9.0},
    ],
}

def display_first_three_purchase_orders():
    keys = list(purchase_orders.keys())
    result = []
    for i in range((3)):
        result.append(keys[i])
    return {"result":result}

def get_purchase_order_details(purchase_order, line_number=None):
    upper = purchase_order.upper()
    if upper not in purchase_orders:
        return {"error": "Purchase order not found"}
    if line_number is None:
        return {"details": purchase_orders[upper]}
    else:
        for line in purchase_orders[upper]:
            if line["line"] == line_number:
                return {"line_details": line}
        return {"error": "Line number not found"}

#need to incorporate this to allow user to edit
def edit_purchase_order_line(purchase_order, line_number, description=None, quantity=None, unit_price=None):
    upper = purchase_order.upper()
    if upper not in purchase_orders:
        return "Purchase order not found"
    for line in purchase_orders[upper]:
        if line["line"] == line_number:
            if description is not None:
                line["description"] = description
            if quantity is not None:
                line["quantity"] = quantity
            if unit_price is not None:
                line["unit_price"] = unit_price
            return "Line edited successfully"
    return "Line number not found"


def run_conversation():
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": "Can you show me the first three purchase orders in a list?"}] #start by displaying first 3 purchase orders
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_purchase_order_details",
                "description": "Get details of a specified purchase order", #important to be specific and clear
                "parameters": {
                    "type": "object",
                    "properties": {
                        "purchase_order": {
                            "type": "string",
                            "description": "The purchase order number, e.g., PON123",
                        }
                    },
                    "required": ["purchase_order"],
                },
            },
        },
         {
        "type": "function",
        "function": {
            "name": "display_first_three_purchase_orders",
            "description": "Display the first three purchase orders",
            "parameters": {},  # No parameters for this function
        },
    },
    ]
    
    while True:  #put the api call inside a loop  so it continues as long as user is providing input
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=messages,
            tools=tools, #give the function tools to the api call
            tool_choice="auto",  # auto is default, but we'll be explicit; auto means we will let LLM decide which function should 
            #be called based on the user message rather than assigning it ourselves statically
        )
        response_message = response.choices[0].message  #first response from the model from the initial message at top
        tool_calls = response_message.tool_calls   #the response may include a request to call a function (we specifically asked
        #it to "show the first 3 pos" so it infers it has to call that)
        #print("Tool calls:", tool_calls)
        
        # Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "get_purchase_order_details": get_purchase_order_details,
                "display_first_three_purchase_orders": display_first_three_purchase_orders,
            } 
            messages.append(response_message)  # extend conversation with assistant's reply
            
            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                # function_response = function_to_call(
                #     purchase_order=function_args.get("purchase_order")
                # )
                function_response = function_to_call(**function_args)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        #"content": function_response,
                        "content": json.dumps(function_response),
                    }
                )  # extend conversation with function response
            
            #response from the AI model after you've called the function it requested and 
            #added the function's response to the conversation. It's the AI's response to the function's output
            second_response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=messages,
            )
            print(second_response.choices[0].message.content)
            #return second_response.choices[0].message.content

            user_input = input("Please enter the purchase order and line number (if applicable), separated by a space: ")
            po, line = (user_input.split() + [None])[:2]
            line = int(line) if line else None
            messages.append({"role": "user", "content": f"Show me the details of purchase order {po} line {line} in a json format." })



# Run conversation and print response
# while True:
#     run_conversation()
run_conversation()
