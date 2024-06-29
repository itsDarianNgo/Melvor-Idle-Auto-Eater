class ThresholdManager:
    def __init__(self):
        self.health_threshold_percentage = 0.5  # Default to 50%
        self.max_health = 1000  # Default max health, to be updated dynamically

    def set_threshold_percentage(self, percentage):
        if 0 < percentage <= 1:
            self.health_threshold_percentage = percentage

    def get_threshold_flat(self):
        return self.health_threshold_percentage * self.max_health

    def update_max_health(self, max_health):
        if max_health > 0:
            self.max_health = max_health
