from .user import (
    create_user,
    update_user,
    get_user_by_email,
    authenticate,
    get_user,
    get_users,
)

from .npc import (
    create_npc,
    get_npc,
    get_npcs,
    update_npc,
    create_npc_relationship,
    update_echo_devotion as update_npc_echo_devotion,
    add_daily_routine,
    get_npc_relationships,
    get_npc_routine,
    get_echo_devotion_history as get_npc_echo_devotion_history,
)

from .settlement import (
    create_settlement,
    get_settlement,
    get_settlements,
    update_settlement,
    create_settlement_location,
    update_settlement_relationship,
    update_echo_devotion as update_settlement_echo_devotion,
    get_settlement_relationships,
    get_settlement_locations,
    get_echo_devotion_history as get_settlement_echo_devotion_history,
)

__all__ = [
    # User operations
    "create_user",
    "update_user",
    "get_user_by_email",
    "authenticate",
    "get_user",
    "get_users",
    
    # NPC operations
    "create_npc",
    "get_npc",
    "get_npcs",
    "update_npc",
    "create_npc_relationship",
    "update_npc_echo_devotion",
    "add_daily_routine",
    "get_npc_relationships",
    "get_npc_routine",
    "get_npc_echo_devotion_history",
    
    # Settlement operations
    "create_settlement",
    "get_settlement",
    "get_settlements",
    "update_settlement",
    "create_settlement_location",
    "update_settlement_relationship",
    "update_settlement_echo_devotion",
    "get_settlement_relationships",
    "get_settlement_locations",
    "get_settlement_echo_devotion_history",
] 