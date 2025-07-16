import json
import os
from typing import Dict, Any, Optional
import datetime
from .expert_analyzer import load_expert_config

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
        Create a default user profile that adapts to the expert domain.
        
        Returns:
            A default user profile dictionary
        """
        # Determine if this is career or business coaching
        try:
            config = load_expert_config()
            domain = config.get('expert_profile', {}).get('expertise_domain', '').lower()
            is_career = 'career' in domain or 'job' in domain
        except:
            is_career = False
        
        if is_career:
            return {
                "career_info": {
                    "name": None,
                    "current_role": None,
                    "target_roles": [],
                    "industry": None,
                    "experience_level": None,
                    "skills": [],
                    "salary_range": None,
                    "career_goals": [],
                    "challenges": []
                },
                "conversation_history": [],
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat()
            }
        else:
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
        Update a field in the business_info or career_info section.
        
        Args:
            field: The field to update
            value: The new value
        """
        info_key = "career_info" if "career_info" in self.profile else "business_info"
        if field in self.profile[info_key]:
            self.profile[info_key][field] = value
            self.save()
        else:
            raise KeyError(f"Field {field} not found in {info_key}")
    
    def add_to_list(self, field: str, value: Any) -> None:
        """
        Add a value to a list field in business_info or career_info.
        
        Args:
            field: The list field to add to
            value: The value to add
        """
        info_key = "career_info" if "career_info" in self.profile else "business_info"
        if field in self.profile[info_key] and isinstance(self.profile[info_key][field], list):
            if value not in self.profile[info_key][field]:
                self.profile[info_key][field].append(value)
                self.save()
        else:
            raise KeyError(f"Field {field} not found or not a list in {info_key}")
    
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
        Adapts to career or business context.
        
        Returns:
            A string representation of the user profile
        """
        if "career_info" in self.profile:
            return self._format_career_profile()
        else:
            return self._format_business_profile()
    
    def _format_career_profile(self) -> str:
        """
        Format career-specific profile information.
        
        Returns:
            Formatted career profile string
        """
        career_info = self.profile["career_info"]
        
        formatted = "User Career Profile:\n"
        
        if career_info["name"]:
            formatted += f"- Name: {career_info['name']}\n"
        
        if career_info["current_role"]:
            formatted += f"- Current Role: {career_info['current_role']}\n"
        
        if career_info["industry"]:
            formatted += f"- Industry: {career_info['industry']}\n"
        
        if career_info["experience_level"]:
            formatted += f"- Experience Level: {career_info['experience_level']}\n"
        
        if career_info["target_roles"]:
            formatted += "- Target Roles:\n"
            for role in career_info["target_roles"]:
                formatted += f"  - {role}\n"
        
        if career_info["skills"]:
            formatted += "- Skills:\n"
            for skill in career_info["skills"]:
                formatted += f"  - {skill}\n"
        
        if career_info["salary_range"]:
            formatted += f"- Salary Range: {career_info['salary_range']}\n"
        
        if career_info["career_goals"]:
            formatted += "- Career Goals:\n"
            for goal in career_info["career_goals"]:
                formatted += f"  - {goal}\n"
        
        if career_info["challenges"]:
            formatted += "- Challenges:\n"
            for challenge in career_info["challenges"]:
                formatted += f"  - {challenge}\n"
        
        return formatted
    
    def _format_business_profile(self) -> str:
        """
        Format business-specific profile information.
        
        Returns:
            Formatted business profile string
        """
        business_info = self.profile["business_info"]
        
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
        Extract structured information from user messages based on domain.
        
        Args:
            message: The user's message
            assistant_response: The assistant's response
        """
        if "career_info" in self.profile:
            self._extract_career_info(message)
        else:
            self._extract_business_info(message)
        
        # Add the conversation to history
        self.add_conversation(message, assistant_response)
    
    def _extract_career_info(self, message: str) -> None:
        """
        Extract career-specific information from messages.
        
        Args:
            message: The user's message
        """
        message_lower = message.lower()
        
        # Extract role information
        if "current role" in message_lower or "current position" in message_lower:
            # Simple extraction - in a real implementation, this would use NLP
            pass
        
        # Extract salary information
        import re
        salary_matches = re.findall(r'\$(\d+,?\d*)k?', message)
        if salary_matches:
            for match in salary_matches:
                salary = match.replace(',', '')
                self.profile["career_info"]["salary_range"] = f"${salary}"
                self.save()
        
        # Extract skills
        skill_keywords = ["skill", "experience with", "good at", "proficient in"]
        for keyword in skill_keywords:
            if keyword in message_lower:
                # Simple extraction - would be more sophisticated in real implementation
                break
    
    def _extract_business_info(self, message: str) -> None:
        """
        Extract business-specific information from messages.
        
        Args:
            message: The user's message
        """
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
                self.profile["business_info"]["pricing"]["recent_sale"] = f"${price}"
                self.save() 