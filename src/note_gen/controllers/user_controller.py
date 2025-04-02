"""
Controller for user operations.

This controller handles the business logic for user operations,
including user authentication, registration, and profile management.
"""

from typing import List, Optional, Dict, Any

from note_gen.database.repositories.base import BaseRepository
from note_gen.models.user import User


class UserController:
    """Controller for user operations."""

    def __init__(self, user_repository: BaseRepository):
        """
        Initialize the user controller.

        Args:
            user_repository: Repository for user data access
        """
        self.user_repository = user_repository

    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            The user if found, None otherwise
        """
        return await self.user_repository.find_one(user_id)

    async def get_all_users(self) -> List[User]:
        """
        Get all users.

        Returns:
            List of all users
        """
        return await self.user_repository.find_many()

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user.

        Args:
            user_data: Data for the new user

        Returns:
            The created user
        """
        # Check if username already exists
        existing_users = await self.user_repository.find_many({"username": user_data["username"]})
        if existing_users:
            raise ValueError(f"Username already exists: {user_data['username']}")

        # Create the user
        user = User(**user_data)
        return await self.user_repository.create(user)

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update a user.

        Args:
            user_id: ID of the user to update
            user_data: Data to update the user with

        Returns:
            The updated user if found, None otherwise
        """
        # Get the user
        user = await self.get_user(user_id)
        if not user:
            return None

        # Update the user
        for key, value in user_data.items():
            setattr(user, key, value)

        # Save the user
        return await self.user_repository.update(user_id, user)

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.

        Args:
            user_id: ID of the user to delete

        Returns:
            True if the user was deleted, False otherwise
        """
        return await self.user_repository.delete(user_id)

    async def get_current_user(self) -> User:
        """
        Get the current user.

        Returns:
            The current user
        """
        # This would typically use authentication to get the current user
        # For now, we'll return a placeholder user
        return User(
            username="current_user",
            email="current@example.com",
            full_name="Current User"
        )

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: Username of the user to retrieve

        Returns:
            The user if found, None otherwise
        """
        users = await self.user_repository.find_many({"username": username})
        return users[0] if users else None
