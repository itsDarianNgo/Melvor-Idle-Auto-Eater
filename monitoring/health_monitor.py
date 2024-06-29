from PyQt5.QtCore import QTimer
from management.threshold_manager import ThresholdManager
from management.food_manager import FoodManager
from monitoring.attack_monitor import AttackMonitor

class HealthMonitor:
    def __init__(self, web_engine_view, health_label, max_health_label, danger_label, threshold_manager, food_manager):
        self.web_engine_view = web_engine_view
        self.health_label = health_label
        self.max_health_label = max_health_label
        self.danger_label = danger_label
        self.threshold_manager = threshold_manager
        self.food_manager = food_manager
        self.attack_monitor = AttackMonitor(web_engine_view)
        self.init_monitoring()

    def init_monitoring(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_game_ready)
        self.timer.start(1000)  # Check every second if the game object is ready

    def check_game_ready(self):
        self.web_engine_view.page().runJavaScript('typeof game !== "undefined"', self.on_game_ready)

    def on_game_ready(self, game_ready):
        if game_ready:
            self.timer.stop()
            self.start_monitoring()

    def start_monitoring(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_health)
        self.timer.start(100)  # Update every 100ms

    def update_health(self):
        self.web_engine_view.page().runJavaScript('game.combat.player.stats.character.hitpoints', self.check_health)
        self.web_engine_view.page().runJavaScript('game.combat.player.stats._maxHitpoints', self.update_max_health_label)
        self.web_engine_view.page().runJavaScript('game.combat.player.stats.character.manager.enemy.stats._maxHit', self.update_danger_status)

    def check_health(self, current_health):
        self.update_health_label(current_health)
        if current_health is not None:
            self.web_engine_view.page().runJavaScript('game.combat.player.stats.character.manager.enemy.stats._maxHit', lambda enemy_max_damage: self.evaluate_healing(current_health, enemy_max_damage))

    def evaluate_healing(self, current_health, enemy_max_damage):
        if self.should_heal_immediately(current_health, enemy_max_damage):
            self.perform_healing(current_health)
        elif self.should_heal_after_attack(current_health):
            self.attack_monitor.get_player_attack_status(lambda player_status: self.check_attack_and_heal(current_health, player_status))

    def should_heal_immediately(self, current_health, enemy_max_damage):
        # Prioritize healing if the player's health is below the enemy's max damage
        return current_health <= enemy_max_damage

    def should_heal_after_attack(self, current_health):
        # Heal based on threshold if the player's health is below the threshold but above the enemy's max damage
        return current_health <= self.threshold_manager.get_threshold_flat()

    def check_attack_and_heal(self, current_health, player_status):
        if self.should_heal_casually(player_status):
            self.perform_healing(current_health)

    def should_heal_casually(self, player_status):
        # Heal if the player's current tick count is between max and max - 4
        return player_status['current'] <= player_status['max'] and player_status['current'] > player_status['max'] - 4

    def perform_healing(self, current_health):
        max_health = self.threshold_manager.max_health
        health_needed = max_health - current_health

        best_food = self.food_manager.select_food(health_needed)
        if best_food:
            self.food_manager.select_food_slot(best_food['slotNumber'])
            qty_needed = (health_needed + best_food['healing'] - 1) // best_food['healing']  # Ceiling division
            qty_to_use = min(qty_needed, best_food['quantity'])
            self.food_manager.use_food(qty_to_use, best_food['name'])

    def update_health_label(self, health):
        if health is not None:
            self.health_label.setText(f"Health: {health}")
        else:
            self.health_label.setText("Health: N/A")

    def update_max_health_label(self, max_health):
        if max_health is not None:
            self.max_health_label.setText(f"Max Health: {max_health}")
            self.threshold_manager.update_max_health(max_health)
        else:
            self.max_health_label.setText("Max Health: N/A")

    def update_danger_status(self, enemy_max_damage):
        if enemy_max_damage is not None:
            self.web_engine_view.page().runJavaScript('game.combat.player.stats.character.hitpoints', lambda current_health: self.check_danger(current_health, enemy_max_damage))
        else:
            self.danger_label.setText("In Danger: N/A")

    def check_danger(self, current_health, enemy_max_damage):
        if current_health is not None and enemy_max_damage is not None:
            in_danger = current_health <= enemy_max_damage
            self.danger_label.setText(f"In Danger: {in_danger}")
        else:
            self.danger_label.setText("In Danger: N/A")
