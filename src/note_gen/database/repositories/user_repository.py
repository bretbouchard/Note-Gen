"""User repository implementation for the MCP architecture."""
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from note_gen.database.repositories.mongodb_repository import MongoDBRepository
from note_gen.models.user import User

class UserRepository(MongoDBRepository[User]):
    """Repository for user operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """
        Initialize the user repository.
        
        Args:
            collection: MongoDB collection to use
        """
        super().__init__(collection, User)

    async def find_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by username.
        
        Args:
            username: Username of the user to find
            
        Returns:
            User if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"username": username})
            return self._convert_to_model(doc) if doc else None
        except Exception as e:
            # Log the error
            print(f"Error finding user by username: {e}")
            return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email.
        
        Args:
            email: Email of the user to find
            
        Returns:
            User if found, None otherwise
        """
        try:
            doc = await self.collection.find_one({"email": email})
            return self._convert_to_model(doc) if doc else None
        except Exception as e:
            # Log the error
            print(f"Error finding user by email: {e}")
            return None

    async def find_active_users(self) -> List[User]:
        """
        Find all active users.
        
        Returns:
            List of active users
        """
        try:
            cursor = self.collection.find({"is_active": True})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding active users: {e}")
            return []

    async def find_superusers(self) -> List[User]:
        """
        Find all superusers.
        
        Returns:
            List of superusers
        """
        try:
            cursor = self.collection.find({"is_superuser": True})
            documents = await cursor.to_list(length=None)
            return [self._convert_to_model(doc) for doc in documents if doc]
        except Exception as e:
            # Log the error
            print(f"Error finding superusers: {e}")
            return []

    async def update_password(self, user_id: str, hashed_password: str) -> Optional[User]:
        """
        Update a user's password.
        
        Args:
            user_id: ID of the user to update
            hashed_password: New hashed password
            
        Returns:
            Updated user if found, None otherwise
        """
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"hashed_password": hashed_password}}
            )
            
            if result.matched_count > 0:
                updated_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
                return self._convert_to_model(updated_doc) if updated_doc else None
            return None
        except Exception as e:
            # Log the error
            print(f"Error updating user password: {e}")
            return None
