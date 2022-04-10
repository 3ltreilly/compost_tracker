from django.apps import AppConfig


class PileTrackerConfig(AppConfig):
    name = "pile_tracker"

    def ready(self):
        print("I'm ready")
