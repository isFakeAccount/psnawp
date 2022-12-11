BASE_PATH = {
    "base_uri": "https://ca.account.sony.com/api",
    "profile_uri": "https://m.np.playstation.com/api/userProfile/v1/internal/users",
    "account_uri": "https://dms.api.playstation.com/api",
    "legacy_profile_uri": "https://us-prof.np.community.playstation.net/userProfile/v1/users",
    "gaming_lounge": "https://m.np.playstation.com/api/gamingLoungeGroups/v1",
    "group_messaging": "https://us-gmsg.np.community.playstation.net/groupMessaging/v1",
    "universal_search": "https://m.np.playstation.com/api/search/v1/universalSearch",
    "game_titles": "https://m.np.playstation.com/api/catalog/v2/titles",
    "trophies": "https://m.np.playstation.com/api/trophy/v1",
    "games_list": "https://m.np.playstation.com/api/gamelist/v2",
}

API_PATH = {
    # Auth Endpoints
    "oauth_code": "/authz/v3/oauth/authorize",
    "access_token": "/authz/v3/oauth/token",
    # Client/User Endpoint
    "my_account": "/v1/devices/accounts/me",
    "profiles": "/{account_id}/profiles",
    "legacy_profile": "/{online_id}/profile2",
    "friends_list": "/me/friends",
    "friends_summary": "/me/friends/{account_id}/summary",
    "available_to_play": "/me/friends/subscribing/availableToPlay",
    "blocked_users": "/me/blocks",
    "basic_presences": "/basicPresences",
    # Group Endpoints
    "my_groups": "/members/me/groups",
    "group_settings": "/groups/{group_id}",
    "create_group": "/groups",
    "group_members": "/members/me/groups/{group_id}",
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
}
