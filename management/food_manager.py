from PyQt5.QtCore import QTimer

class FoodManager:
    def __init__(self, web_engine_view):
        self.web_engine_view = web_engine_view
        self.food_inventory = {}
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.full_update_food_inventory)
        self.start_auto_update()
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self.sync_food_inventory)
        self.start_sync()

    def start_auto_update(self):
        # Start the timer to update food inventory every 30 seconds
        self.update_timer.start(30000)  # 30,000 ms = 30 seconds

    def start_sync(self):
        # Start the timer to sync food inventory every 5 minutes
        self.sync_timer.start(300000)  # 300,000 ms = 5 minutes

    def full_update_food_inventory(self):
        self.web_engine_view.page().runJavaScript('''(function() {
            const slots = game.combat.player.stats.character.food.slots;
            return slots.map(slot => {
                if (slot.item) {
                    return {
                        name: slot.item._name,
                        healing: slot.item.healsFor * 10,
                        quantity: slot.quantity,
                        slotNumber: slots.indexOf(slot)
                    };
                } else {
                    return null;
                }
            }).filter(food => food !== null);
        })()''', self.set_food_inventory)

    def set_food_inventory(self, inventory):
        if inventory is not None:
            self.food_inventory = {food['name']: food for food in inventory}

    def sync_food_inventory(self):
        self.full_update_food_inventory()

    def use_food(self, qty, food_name):
        if food_name in self.food_inventory:
            if self.food_inventory[food_name]['quantity'] >= qty:
                self.food_inventory[food_name]['quantity'] -= qty
                self.web_engine_view.page().runJavaScript(f'game.combat.player.stats.character.eatFood({qty})', self.update_food_inventory_after_use)

    def update_food_inventory_after_use(self, result):
        # Update the inventory immediately after using food
        self.full_update_food_inventory()

    def select_food_slot(self, slot):
        self.web_engine_view.page().runJavaScript(f'game.combat.player.stats.character.selectFood({slot})')

    def select_food(self, health_needed):
        best_food = None

        # Find the food that best matches the health needed without excessive waste
        for food in self.food_inventory.values():
            if food['quantity'] > 0 and food['healing'] >= health_needed:
                if best_food is None or food['healing'] < best_food['healing']:
                    best_food = food

        # If no perfect match is found, choose the best available option
        if best_food is None:
            for food in self.food_inventory.values():
                if food['quantity'] > 0 and (best_food is None or food['healing'] > best_food['healing']):
                    best_food = food

        return best_food
