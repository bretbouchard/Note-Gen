"""
Presenter for user data.

This presenter formats user data for API responses,
ensuring a clean separation between the business logic and the presentation layer.
"""

from typing import List, Dict, Any

from note_gen.models.user import User


class UserPresenter:
    """Presenter for user data."""

    @staticmethod
    def present(user: User) -> Dict[str, Any]:
        """
        Format a user for API response.

        Args:
            user: The user to format

        Returns:
            Formatted user data
        """
        return {
            "id": str(user.id) if hasattr(user, "id") else None,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "disabled": user.disabled if hasattr(user, "disabled") else False,
            "created_at": user.created_at.isoformat() if hasattr(user, "created_at") else None,
            "updated_at": user.updated_at.isoformat() if hasattr(user, "updated_at") else None,
        }

    @staticmethod
    def present_many(users: List[User]) -> List[Dict[str, Any]]:
        """
        Format multiple users for API response.

        Args:
            users: The users to format

        Returns:
            List of formatted user data
        """
        return [UserPresenter.present(user) for user in users]

    @staticmethod
    def present_profile(user: User) -> Dict[str, Any]:
        """
        Format a user profile for API response.

        Args:
            user: The user to format

        Returns:
            Formatted user profile data
        """
        # Profile view might include additional data like preferences, settings, etc.
        profile = UserPresenter.present(user)

        # Add profile-specific fields
        profile.update({
            "preferences": user.preferences if hasattr(user, "preferences") else {},
            "settings": user.settings if hasattr(user, "settings") else {},
        })

        return profile
