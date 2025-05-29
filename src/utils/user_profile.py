import json
import os
from typing import Dict, Any, Optional
import datetime

class UserProfile:
    """
    Manages user information learned through conversations.
    """
    def __init__(self, profile_path: str = "./user_profile.json"):
        """
        Initialize the user profile.
        
        Args:
            profile_path: Path to the user profile JSON file
        """
        self.profile_path = profile_path
        self.profile = self._load_profile()
        
    def _load_profile(self) -> Dict[str, Any]:
        """
        Load the user profile from disk.
        
        Returns:
            The user profile as a dictionary
        """
        if os.path.exists(self.profile_path):
            try:
                with open(self.profile_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode profile at {self.profile_path}, creating new one")
                return self._create_default_profile()
        else:
            return self._create_default_profile()
    
    def _create_default_profile(self) -> Dict[str, Any]:
        """
        Create a default user profile.
        
        Returns:
            A default user profile dictionary
        """
        return {
            "business_info": {
                "name": None,
                "type": None,
                "services": [],
                "pricing": {},
                "clients": [],
                "goals": [],
                "challenges": []
            },
            "conversation_history": [],
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat()
        }
    
    def save(self) -> None:
        """
        Save the user profile to disk.
        """
        # Update timestamp
        self.profile["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save to disk
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=2)
    
    def update_business_info(self, field: str, value: Any) -> None:
        """
        Update a field in the business_info section.
        
        Args:
            field: The field to update
            value: The new value
        """
        if field in self.profile["business_info"]:
            self.profile["business_info"][field] = value
            self.save()
        else:
            raise KeyError(f"Field {field} not found in business_info")
    
    def add_to_list(self, field: str, value: Any) -> None:
        """
        Add a value to a list field in business_info.
        
        Args:
            field: The list field to add to
            value: The value to add
        """
        if field in self.profile["business_info"] and isinstance(self.profile["business_info"][field], list):
            if value not in self.profile["business_info"][field]:
                self.profile["business_info"][field].append(value)
                self.save()
        else:
            raise KeyError(f"Field {field} not found or not a list in business_info")
    
    def add_conversation(self, user_message: str, assistant_message: str) -> None:
        """
        Add a conversation exchange to the history.
        
        Args:
            user_message: The user's message
            assistant_message: The assistant's response
        """
        self.profile["conversation_history"].append({
            "user": user_message,
            "assistant": assistant_message,
            "timestamp": datetime.datetime.now().isoformat()
        })
        self.save()
    
    def get_formatted_profile(self) -> str:
        """
        Get a formatted string representation of the user profile.
        
        Returns:
            A string representation of the user profile
        """
        business_info = self.profile["business_info"]
        
        # Format business info
        formatted = "User Business Profile:\n"
        
        if business_info["name"]:
            formatted += f"- Business Name: {business_info['name']}\n"
        
        if business_info["type"]:
            formatted += f"- Business Type: {business_info['type']}\n"
        
        if business_info["services"]:
            formatted += "- Services:\n"
            for service in business_info["services"]:
                formatted += f"  - {service}\n"
        
        if business_info["pricing"]:
            formatted += "- Pricing:\n"
            for service, price in business_info["pricing"].items():
                formatted += f"  - {service}: {price}\n"
        
        if business_info["clients"]:
            formatted += "- Clients:\n"
            for client in business_info["clients"]:
                formatted += f"  - {client}\n"
        
        if business_info["goals"]:
            formatted += "- Goals:\n"
            for goal in business_info["goals"]:
                formatted += f"  - {goal}\n"
        
        if business_info["challenges"]:
            formatted += "- Challenges:\n"
            for challenge in business_info["challenges"]:
                formatted += f"  - {challenge}\n"
        
        return formatted
    
    def extract_info_from_message(self, message: str, assistant_response: str) -> None:
        """
        Use the LLM itself to extract structured information from user messages.
        This would typically call an external API to process the message.
        
        Args:
            message: The user's message
            assistant_response: The assistant's response
        """
        # For demonstration purposes, we'll just look for key phrases and extract simple info
        
        # Extract service information
        services = []
        if "website" in message.lower() or "website upgrade" in message.lower():
            services.append("Website Development/Upgrade")
        if "digital" in message.lower() and "makeover" in message.lower():
            services.append("Digital Presence Makeover")
        
        for service in services:
            self.add_to_list("services", service)
        
        # Extract pricing information
        import re
        price_matches = re.findall(r'\$(\d+,?\d*)', message)
        if price_matches:
            for match in price_matches:
                price = int(match.replace(',', ''))
                # We don't know what service this is for, so we'll use a general key
                self.profile["business_info"]["pricing"]["recent_sale"] = f"${price}"
                self.save()
        
        # Add the conversation to history
        self.add_conversation(message, assistant_response) 