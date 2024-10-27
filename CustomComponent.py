from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Data
from permit import Permit

import asyncio

class PermissionCheckComponent(Component):
    display_name = "Permission Check Component"
    description = "Check user permissions with Permit.io for dynamic role-based access control."
    documentation: str = "https://docs.permit.io"
    icon = "custom_components"
    name = "PermissionCheckComponent"

    # Inputs from Langflow
    inputs = [
        MessageTextInput(name="user_name", display_name="User ID", value=""),
        MessageTextInput(name="prompt", display_name="Prompt", value=""),
    ]

    # Outputs: either allowed prompt or permission denied message
    outputs = [
        Output(display_name="Output", name="output", method="build_output"),
    ]

    async def build_output(self) -> Message:
        # Initialize Permit client inside the method
        permit = Permit(
            pdp="http://localhost:7766",  # replace with your actual PDP URL
            token="permit_key_AuNPz3FSdCtQqAUj1g2qA434feVq26YPk3e5AMvKRxt7pexKJZzCu9nIPfT7Jb2F3MRurqHXacye1GjcRUNpbw"
        )

        # Retrieve inputs from Langflow's inputs
        user_name = self.user_name  # Accessing user_name input
        prompt = self.prompt     # Accessing the prompt input

        # Debugging logs
        print(f"User Name: {user_name}")
        print(f"Prompt: {prompt}")

        # Define the resource you want to check permissions on (e.g., 'chatbot')
        resource = "chatbot"

        # Message content to return
        message_content = ""
        
        if not user_name or not prompt:
            return Message(text="Error: Missing user name, subscriber type, or prompt input.")

        # Dictionary of users
        users = {
            "John": {
                "key": "user456",
                "first_name": "John",
                "last_name": "Smith",
                "email": "john@company.com",
                "attributes": {
                    "subscriber_type": "Free",
                    "department": "viewer"
                }
            },
            "Max": {
                "key": "user111",
                "first_name": "Max",
                "last_name": "James",
                "email": "max@company.com",
                "attributes": {
                    "subscriber_type": "Premium",
                    "department": "viewer"
                }
            },
            "Siddhesh": {
                "key": "user123",
                "first_name": "Siddhesh",
                "last_name": "Bangar",
                "email": "sid@company.com",
                "attributes": {
                    "subscriber_type": "Premium",
                    "department": "admin"
                }
            }
        }

        # Search for the user based on both `user_name` and `country`
        user = None
        for user_data in users.values():
            if user_data["first_name"].lower() == user_name.lower():
                user = user_data
                break

        # If the user is not found, return an error message
        if not user:
            return Message(text=f"User {user_name} not found.")

        try:
            # Check if the user has 'write' permissions
            permitted = await permit.check(
                user=user["key"],
                action="write",
                resource=resource,
            )

            if permitted:
                # If user has write access, allow the prompt to proceed
                message_content = prompt
            else:
                message_content = f"Give a response that the User {user_name} do not access to the Chat Bot."

        except Exception as e:
            message_content = f"Error checking permissions: {str(e)}"

        # Return the message as output
        return Message(text=message_content)
