from django.apps import AppConfig


class LeaderboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaderboard'

    def ready(self):
        import communityLeaderboard.server.leaderboard.fetch_leetcode_data
