"""Path Endpoints and domains for the PlayStation API."""

from typing import Final

#: BASE_PATH contains common base URIs for PlayStation API endpoints.
#: It centralizes frequently used URL paths, making the code cleaner and easier to maintain.
BASE_PATH: Final[dict[str, str]] = {
    "base_uri": "https://ca.account.sony.com/api",
    "profile_uri": "https://m.np.playstation.com/api/userProfile/v1/internal/users",
    "profile_uri_v2": "https://m.np.playstation.com/api/userProfile/v2/internal/users",
    "account_uri": "https://dms.api.playstation.com/api",
    "legacy_profile_uri": "https://us-prof.np.community.playstation.net/userProfile/v1/users",
    "gaming_lounge": "https://m.np.playstation.com/api/gamingLoungeGroups/v1",
    "universal_search": "https://m.np.playstation.com/api/search/v1/universalSearch",
    "game_titles": "https://m.np.playstation.com/api/catalog/v2/titles",
    "trophies": "https://m.np.playstation.com/api/trophy/v1",
    "games_list": "https://m.np.playstation.com/api/gamelist/v2",
    "graph_ql": "https://m.np.playstation.com/api/graphql/v1/op",
    "cpss": "https://m.np.playstation.com/api/cpss",
    # Future use
    "sony_account_ca_base_url": "https://ca.account.sony.com",
    "psn_np_mobile_base_url": "https://m.np.playstation.com",
    "psn_dms_api_base_url": "https://dms.api.playstation.com",
    "psn_us_profile_community_base_url": "https://us-prof.np.community.playstation.net",
}

#: API_PATH contains the relative paths for various PlayStation API endpoints, organized by categories
#: such as authentication, client/user operations, groups, games, and trophies. These paths are used
#: to construct full URLs for API requests.
API_PATH: Final[dict[str, str]] = {
    # Auth Endpoints
    "oauth_code": "/authz/v3/oauth/authorize",
    "access_token": "/authz/v3/oauth/token",
    # Client/User Endpoint
    "my_account": "/v1/devices/accounts/me",
    "profiles": "/{account_id}/profiles",
    "legacy_profile": "/{online_id}/profile2",
    "friends_list": "/{account_id}/friends",
    "friends_request": "/{account_id}/friends/receivedRequests",
    "manage_friendship": "/me/friends/{account_id}",
    "friends_summary": "/me/friends/{account_id}/summary",
    "available_to_play": "/me/friends/subscribing/availableToPlay",
    "blocked_users": "/me/blocks",
    "basic_presences": "/basicPresences",
    "share_profile": "/v1/share/profile/{account_id}",
    # Group Endpoints
    "my_groups": "/members/me/groups",
    "group_settings": "/groups/{group_id}",
    "create_group": "/groups",
    "group_members": "/members/me/groups/{group_id}",
    "invite_members": "/groups/{group_id}/invitees",
    "kick_member": "/groups/{group_id}/members/{account_id}",
    "send_group_message": "/groups/{group_id}/threads/{group_id}/messages",
    "conversation": "/members/me/groups/{group_id}/threads/{group_id}/messages",
    "leave_group": "/groups/{group_id}/members/me",
    # Game Title Details
    "title_concept": "/{title_id}/concepts",
    # Trophy Endpoints
    "trophy_titles": "/users/{account_id}/trophyTitles",
    "trophies_for_title": "/npCommunicationIds/{np_communication_id}/trophyGroups/{trophy_group_id}/trophies",
    "trophies_earned_for_title": "/users/{account_id}/npCommunicationIds/{np_communication_id}/trophyGroups/{trophy_group_id}/trophies",
    "trophy_summary": "/users/{account_id}/trophySummary",
    "title_trophy_group": "/npCommunicationIds/{np_communication_id}/trophyGroups",
    "user_title_trophy_group": "/users/{account_id}/npCommunicationIds/{np_communication_id}/trophyGroups",
    "trophy_titles_for_title": "/users/{account_id}/titles/trophyTitles",
    # User Title Data
    "user_game_data": "/users/{account_id}/titles",
    # Entitlements
    "entitlements": "/api/entitlement/v2/users/me/internal/entitlements",
}
