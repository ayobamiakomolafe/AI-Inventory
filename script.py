import json
from groq import Groq
import os
import pandas as pd
import numpy as np
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import io
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive




app = Flask(__name__) 


# Initialize Groq client
client = Groq(api_key = "sk-XXXXXXXXXXXXXXXXXXXXXX")  # Replace with your Groq API key
model = "llama-3.3-70b-versatile"


# Set up Google Drive API credentials and service
SERVICE_ACCOUNT_FILE = 'C:/Users/USER/Desktop/AI invoicing/service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)



def upload_file_to_drive_pydrive(local_path, folder_id=None):
    """
    Upload a file to Google Drive using PyDrive and OAuth2.
    If a file with the same name exists in the target folder, it will be deleted first.
    Optionally specify a folder ID to upload into.
    """
    # Authenticate and create the PyDrive client
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Opens a browser for authentication
    drive = GoogleDrive(gauth)

    file_name = os.path.basename(local_path)

    # Search for existing files with the same name in the folder
    if folder_id:
        query = f"title='{file_name}' and '{folder_id}' in parents and trashed=false"
    else:
        query = f"title='{file_name}' and trashed=false"
    file_list = drive.ListFile({'q': query}).GetList()
    for file in file_list:
        file.Delete()
        print(f"Deleted existing file: {file['title']} (ID: {file['id']})")

    # Upload the new file
    file_metadata = {'title': file_name}
    if folder_id:
        file_metadata['parents'] = [{'id': folder_id}]
    gfile = drive.CreateFile(file_metadata)
    gfile.SetContentFile(local_path)
    gfile.Upload()
    print(f"Uploaded '{local_path}' to Google Drive with file ID: {gfile['id']}")
    return gfile['id']

def download_file_from_drive(file_name, destination_path):
    """
    Download a file from Google Drive by file name using a service account.
    """
    # Search for the file by name
    results = drive_service.files().list(q=f"name='{file_name}' and trashed=false",
                                         spaces='drive',
                                         fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print(f"No file found with name: {file_name}")
        return None
    file_id = items[0]['id']

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()

# def upload_file_to_drive(local_path, drive_folder_id=None):
#     """
#     Upload a file to Google Drive using a service account.
#     If a file with the same name exists in the target folder, it will be deleted first.
#     Optionally specify a folder ID to upload into.
#     """
#     file_name = os.path.basename(local_path)

#     # Build the search query
#     if drive_folder_id:
#         query = f"name='{file_name}' and '{drive_folder_id}' in parents and trashed=false"
#     else:
#         query = f"name='{file_name}' and trashed=false"

#     # Search for existing files with the same name
#     results = drive_service.files().list(q=query, spaces='drive', fields="files(id, name)").execute()
#     items = results.get('files', [])
#     for item in items:
#         # Delete each found file
#         drive_service.files().delete(fileId=item['id']).execute()
#         print(f"Deleted existing file: {item['name']} (ID: {item['id']})")

#     # Upload the new file
#     file_metadata = {'name': file_name}
#     if drive_folder_id:
#         file_metadata['parents'] = [drive_folder_id]
#     media = MediaFileUpload(local_path, resumable=True)
#     file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     return file.get('id')
    

# Define weather tools
def save_data(Product, Selling_Price, Quantity_Stocked, Quantity_Sold):
    download_file_from_drive("Inv-1.xlsx", "C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx")
    try:
        df = pd.read_excel("C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx")

        Quantity_Sold = int(Quantity_Sold)
        Quantity_Stocked = int(Quantity_Stocked)
        Selling_Price = float(Selling_Price)
        Product = str(Product)
        Quantity_Remaining = Quantity_Stocked - Quantity_Sold
        Total_Sold = Selling_Price * Quantity_Sold
        Total_Stocked = Selling_Price * Quantity_Stocked

        # Generate new index value for the first column (assuming it's an auto-incrementing ID)
        if len(df) > 0:
            insert_row = int(df.iloc[:, 0].values[-3]) 
            new_index_value = int(df.iloc[:, 0].values[-3]) + 1
        else:
            new_index_value = 1

        new_row = pd.DataFrame([[new_index_value, Product, Selling_Price, Quantity_Stocked, Quantity_Sold, Quantity_Remaining, Total_Sold, Total_Stocked]],
                            columns=df.columns)

        if insert_row is not None and 0 <= insert_row <= len(df):
            # Insert at specific row
            df1 = df.iloc[:insert_row, :]
            df2 = df.iloc[insert_row:, :]
            df = pd.concat([df1, new_row, df2], ignore_index=True)
        else:
            # Append at the end
            df = pd.concat([df, new_row], ignore_index=True)
        

    
        last_idx = df.index[-1]
        df_ = df.iloc[:-1]
        df.loc[last_idx] = [np.nan, "TOTAL", df_["PRIX DE VENTE"].sum(), df_["QTE STOCK"].sum(), df_["QTE SORTIE"].sum(), df_["QTE RESTANT "].sum(), df_["Total vendu"].sum(), df_["Total attendu"].sum()]

        df.to_excel("C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx", index=False)
        upload_file_to_drive_pydrive("C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx", folder_id="1eGFYwTopxUGDI9QLk-x5WCRyPusp-jiI")
        os.remove("C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx")

        return "Data saved successfully."
    except Exception as e:
        return "Error saving data"


def retrieve_data(user_prompt):
    download_file_from_drive("Inv-1.xlsx", "C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx")
    try:
        df = pd.read_excel("C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx")
        # Get the values from the last index (last row)
        last_row_values = df.iloc[-1].to_dict()
        os.remove("C:/Users/USER/Desktop/AI invoicing/Inv-1.xlsx")
        return last_row_values
    
        
    except Exception as e:
        return "Error retrieving data"
    
system_prompt = """ You are a French-based AI assistant. 
Your primary functions are to assist users in saving and retrieving data from spreadsheets and 
to respond to general inquiries in a helpful and friendly manner.1.**Language and Tone**: Always
respond in French using a friendly and approachable tone.Use polite phrases and expressions to create
a welcoming atmosphere.2.**Spreadsheet Functionality**: When users ask for help with spreadsheets, be
    sure to do what was asked. 3.**General Queries**: For general questions,
you should: - Provide accurate and concise answers.- If the query is complex, break it down into
simpler parts to enhance understanding.- Always encourage 
users to ask follow-up questions if they need more information.
4.**User Engagement**: Maintain user engagement by: - Asking if they need assistance with 
anything else after providing an answer.- Using positive reinforcement to make users feel
valued and appreciated for their inquiries.5.**Limitations**: Clearly communicate your
    limitations where applicable, such as: - If a query goes beyond your capabilities,
politely inform the user and suggest alternative resources.
6.**Data Privacy**: Emphasize the importance of data privacy and security, especially when
handling sensitive spreadsheet information.7.**Context Awareness**: Always consider the 
context of the user’s query to provide relevant responses, adapting your answers based on their needs
and level of understanding.Utilize this prompt to ensure 
all interactions reflect the characteristics of a helpful, friendly, and efficient assistant. """

def run_conversation(user_prompt):
# Define system messages and tools
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt,}
    ]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "save_data",
                "description": "Save data to the spreadsheet when the user provides product details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "Product": {
                            "type": "string",
                            "description": "The name of the product"
                        },
                        "Selling_Price": {
                            "type": "number",
                            "description": "The selling price of the product"
                        },
                        "Quantity_Stocked": {
                            "type": "integer",
                            "description": "The quantity of the product stocked"
                        },
                        "Quantity_Sold": {
                            "type": "integer",
                            "description": "The quantity of the product sold"
                        }
                    },
                    "required": ["Product", "Selling_Price", "Quantity_Stocked", "Quantity_Sold"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "retrieve_data",
                "description": "Retrieve data from the spreadsheet  based on user prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_prompt": {
                            "type": "string",
                            "description": "The user prompt for data retrieval",
                        }
                    },
                    "required": ["user_prompt"],
                },
            },
        },
    
    ]

    # Make the initial request
    response = client.chat.completions.create(
        model=model, messages=messages, tools=tools, tool_choice="auto", max_completion_tokens=4096, temperature=0.5
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Process tool calls
    messages.append(response_message)
    
    if tool_calls:
        available_functions = {
            "save_data": save_data,
            "retrieve_data": retrieve_data,
        }

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)

            messages.append(
                {
                    "role": "tool",
                    "content": str(function_response),
                    "tool_call_id": tool_call.id,
                }
            )

        # Make the final request with tool call results
        final_response = client.chat.completions.create(
            model=model, messages=messages)
        
        response_message = final_response.choices[0].message

    

    return response_message.content



# # if __name__ == "__main__":
# #     while True:
# #         user_input = input("You: ")
# #         if user_input.lower() in ["exit", "quit"]:
# #             print("Exiting the conversation.")
# #             break
# #         response = run_conversation(user_input)
# #         print("Assistant:", response)


@app.route("/webhook", methods=["POST"]) 
def webhook(): 
    # Get incoming message details 
    incoming_msg = request.values.get('Body', '').strip().lower() 
    sender = request.values.get('From', '') 
     
    # Create a response object 
    resp = MessagingResponse() 

    # Log the incoming message
    response = run_conversation(incoming_msg)
    resp.message(response)
    return str(resp) 
 
if __name__ == "__main__": 
    app.run(debug=True) 
