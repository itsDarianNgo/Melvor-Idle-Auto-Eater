class AttackMonitor:
    def __init__(self, web_engine_view):
        self.web_engine_view = web_engine_view

    def get_player_attack_status(self, callback):
        self.web_engine_view.page().runJavaScript('''(function() {
            const timers = game.combat.player.stats.character.timers.act;
            return {
                current: timers._ticksLeft,
                max: timers._maxTicks
            };
        })()''', callback)

    def get_enemy_attack_status(self, callback):
        self.web_engine_view.page().runJavaScript('''(function() {
            const timers = game.combat.player.stats.character.manager.enemy.stats.character.timers.act;
            return {
                current: timers._ticksLeft,
                max: timers._maxTicks
            };
        })()''', callback)
