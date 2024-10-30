"""This module provides CRUD operations for robots."""

import time

from store.app.crud.base import BaseCrud, ItemNotFoundError
from store.app.model import Listing, Robot


class RobotsCrud(BaseCrud):
    """CRUD operations for Robots."""

    async def create_robot(self, robot_data: dict) -> Robot:
        """Create a new robot entry."""
        # Verify listing exists
        listing = await self._get_item(robot_data["listing_id"], Listing)
        if not listing:
            raise ItemNotFoundError(f"Listing with ID {robot_data['listing_id']} not found")

        robot = Robot.create(
            user_id=robot_data["user_id"],
            listing_id=robot_data["listing_id"],
            name=robot_data["name"],
            description=robot_data.get("description"),
        )
        await self._add_item(robot)
        return robot

    async def get_robot(self, robot_id: str) -> Robot:
        """Get a robot by ID."""
        robot = await self._get_item(robot_id, Robot)
        if not robot:
            raise ItemNotFoundError("Robot not found")
        return robot

    async def get_robots_by_user_id(self, user_id: str) -> list[Robot]:
        """Get all robots for a specific user."""
        robots = await self._get_items_from_secondary_index("user_id", user_id, Robot)
        return robots

    async def get_robots_by_listing_id(self, listing_id: str) -> list[Robot]:
        """Get all robots for a specific listing."""
        robots = await self._get_items_from_secondary_index("listing_id", listing_id, Robot)
        return robots

    async def update_robot(self, robot_id: str, update_data: dict) -> Robot:
        """Update a robot's information."""
        robot = await self.get_robot(robot_id)
        if not robot:
            raise ItemNotFoundError("Robot not found")

        update_data["updated_at"] = int(time.time())
        await self._update_item(robot_id, Robot, update_data)

        updated_robot = await self.get_robot(robot_id)
        return updated_robot

    async def delete_robot(self, robot: Robot) -> None:
        """Delete a robot."""
        await self._delete_item(robot)