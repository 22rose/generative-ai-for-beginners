from openai import AzureOpenAI
import os
import dotenv
import datetime

# import dotenv
dotenv.load_dotenv()

# configure Azure OpenAI service client 
client = AzureOpenAI(
  azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"], 
  api_key=os.environ['AZURE_OPENAI_API_KEY'],  
  api_version = "2023-10-01-preview"
  )

deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']


purchase_orders = {
    "PON123": [
        {"line": 1, "description": "Item A", "quantity": 10, "unit_price": 5.0},
        {"line": 2, "description": "Item B", "quantity": 20, "unit_price": 7.5},
    ],
    "PON456": [
        {"line": 1, "description": "Item C", "quantity": 30, "unit_price": 10.0},
    ],
}

def get_invoice(purchase_order_num, line_num, invoice_number):
    for l in purchase_orders[purchase_order_num]:
        if l['line'] == line_num:
            invoice = {
                "invoice_number": invoice_number,
                "invoice_date": str(datetime.datetime.now().date()),
                "email_address": "customer@example.com",
                "final_approval": "Approved",
                "line": line_num,
                "description": l["description"],
                "quantity": l["quantity"],
                "unit_price": l["unit_price"],
            }
    return invoice




prompt = f"""I want you to take on the persona of a helpful assistant answering questions about purchase orders and invoices.Your primary role, however, is creating invoices. you will utilize this data {purchase_orders}. The first thing you will always, always ask the user at the start of the interaction is: 'Which purchase order would you like to invoice?'. It may come in various formats. It should not be case sensitive, so if they user types in 'po123', it is the same as them typing 'PO123' or even 'pO123', 'Po123'. After you ask this question, you should also display the purchase orders to give the user suggestions;like show them PO123 and PO456 in this case. Notice how there is 2 purchase orders: PO123 and PO456. Each purchase order has some number of lines. Notice in PO123 has 2 lines: 1 and 2. PO456 has only 1 line: 1. There are various jargon a user can use to refer to different things in this data. For example ‘po’, ‘PO’, ‘order’, ‘purchase’ could all refer to ‘purchase order’. Thus when a user inputs those, you should treat it as if they are referring to ‘purchase order’ For example, they can ask how many purchase orders are there? You would respond with 'There are 2 purchase orders, PO123, and PO456.' You could even provide more detail about the specific lines in each purchase order if you wanted to. The user can ask you 'How many lines does purchase order PO123 have?', and you would answer with 'Purchase order PO123 has 2 lines', and you may give information about these two lines. If a user has already specified which purchase order they are inquiring about, they may not even have to have the word 'line' in their questions for you. For example, if based on most recent interactions, you know the user is inquiring about PO123, the user may simple say 'how many are there?' and you would say 'there are 2 lines in this specific purchase order'. The user can also ask you questions about the specific line. For example, they could say, 'in purchase order PO123, line 1, what is the quantity?' and you would respond with 'the quantity is 20'. They could ask you 'in that same purchase order, what is the unit price?', and you would answer with 'the unit price in PO123 is 7.5'. The user can also ask you to create an invoice. You can only ever create invoices on specific lines. Never on the whole purchase order. To create an invoice you need to do a couple of things: 1) First ask them which purchase order they would like to invoice. 2) check that the purchase order exists, in this case PO123 and PO456. If the user enters a purchase order that doesnt exist, tell them it doesnt exist and you cannot create an invoice. After this validation, make sure to remember the purchase order they asked for. This is very very important and you will use it as an argument in a function call. 3)if the purchase order exists, check if the purchase order has more than 2 lines. If it does, show the lines to the user and ask the user which line they would like to invoice. Their answer could be in various forms. They could specifically say 'line 1' or just '1' or 'one'. This should all be treated as they want you to invoice line 1 of that specific purchase order. Keep track of this line number as well. Again it is very very important as you will use it in a function call. 4) when they answer, you should now ask for an invoice number. Remember this number, it is very very important as you will use it in a function call. 5)Now you can finally create an invoice based on the data you collected. You will call the get_invoice function, passing in the input you collected as the arguments: get_invoice(purchase_order_num, line_num, invoice_number). The function itself returns an invoice object. You should output this exact object with no additions or subtractions in a JSON format. Do not do your own thing, just output the result of this function call. 6)If the user says they want to invoice a purchase order and you see the purchase order only has one line, you should automatically start the process of making the purchase order on that line. Remember to ask for an invoice number first though and then proceed. So the only difference here is that you do not need to ask the user to specify which line number to invoice if there is only one line number. So for example, if a user tells you 'I want to create an invoice on PO456', or 'invoice on PO456', 'create invoice PO456', you will analyze the data and notice that PO456 has only 1 line. Thus you now ask the user, 'what is the invoice number'. They will input it and you will remember the number. The user may input in various forms. For example, they could just type in the number. or they could specifically say 'the invoice number is ...' or 'invoice number: ...', 'IN:...' What you should get out of these examples is the user may input them in various ways so you just have to know that once you have asked them for the invoice number, they will provide it to you in some fashion. You will now use the user-inputed invoice number along with the purchase order and the sole line number to call the get_invoice function with the respective parameters: getinvoice(purchase_order_num, line_num, invoice_number). The function itself returns an invoice object with various fields. You should output this exact object. Do not add or subtract whatever you feel like. Just simply output the result of the function call. 7)A user also cannot ask you to invoice a line number that does not exist in a specific purchase order. So for example, if a user asks you to invoice line 3 of purchase order PO123, you should tell them the line does not exist and thus an invoice cannot be created."""
messages = [{"role": "system", "content": prompt}]

while True:  
    question = input("your input: ")
    messages.append({"role": "user", "content": question})
    response = client.chat.completions.create(model=deployment, messages=messages, temperature=0.5, max_tokens = 150)
    output = response.choices[0].message.content
    print(output)


#this one just uses a very long prompt; it seems to call the function fine but its not using the same mechanism as version3