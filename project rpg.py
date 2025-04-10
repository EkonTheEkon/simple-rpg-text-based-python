import random

class Player:
    def __init__(self, name, player_class):
        self.name = name
        self.player_class = player_class
        self.xp = 0
        self.gold = 1000
        self.level = 1
        self.skills = {}
        self.inventory_items = []
        self.equipped_items = {}
        self.equipped_accessories = []
        self.inventory_potions = []
        self.step_count = 0
        self.buff_debuff_manager = BuffDebuffManager()
        self.base_crit_chance = 0.1
        self.base_crit_damage = 2
        self.passive = None
        self.max_health = 100  # Initialize max health
        self.speed = 0  # Initialize speed
        self.set_base_stats(player_class)

    def set_base_stats(self, player_class):
        if player_class == "Warrior":
            self.health = 150
            self.max_health = 150
            self.attack = 15
            self.defense = 15
            self.speed = 30  # Set base speed
            self.skills = {
                "Slash": {"damage": 15, "chance": 0.8},  # 80% chance to deal 15 damage
                "Shield Bash": {"damage": 20, "chance": 0.5, "debuff": {"type": "Stun", "duration": 1}}
            }
            self.passive = "Berserk"  # Increases attack when health is low
        elif player_class == "Mage":
            self.health = 80
            self.max_health = 80
            self.attack = 30
            self.defense = 10
            self.speed = 40  # Set base speed
            self.skills = {
                "Fireball": {"damage": 20, "chance": 0.7, "debuff": {"type": "Burn", "amount": 5, "duration": 3}},  # 70% chance to deal 20 damage
                "Heal": {"heal": 15, "chance": 1}  # 100% chance to heal 15 health
            }
            self.passive = "Mana Shield"  # Reduces damage taken when health is low
        elif player_class == "Rogue":
            self.health = 100
            self.max_health = 100
            self.attack = 20
            self.defense = 7
            self.speed = 50  # Set base speed
            self.base_crit_chance += 0.2
            self.base_crit_damage += 1
            self.skills = {
                "Backstab": {"damage": 20, "chance": 0.5, "debuff": {"type": "Defense Down", "amount": 5, "duration": 3}},  # 50% chance to deal 40 damage and decrease defense
                "Execute": {"damage": 50, "chance": 0.3}  # 30% chance to deal 50 damage
            }
            self.passive = "Evasion"  # Increases chance to dodge attacks
        elif player_class == "Knight":
            self.health = 100
            self.max_health = 100
            self.attack = 20
            self.defense = 10
            self.speed = 20  # Set base speed

    def take_damage(self, damage):
        dodge_chance = self.speed / 100  # Calculate dodge chance based on speed
        if random.random() < dodge_chance:
            print(f"{self.name} dodged the attack!")
            return
        if self.passive == "Evasion" and random.random() < 0.2:  # 20% chance to dodge
            print(f"{self.name} dodged the attack!")
            return
        if self.passive == "Mana Shield" and self.health < 0.3 * self.health:
            damage = int(damage * 0.7)  # Reduce damage by 30%
        self.health -= max(0, damage - self.defense)

    def is_alive(self):
        return self.health > 0

    def earn_xp(self, amount):
        self.xp += amount

    def earn_gold(self, amount):
        self.gold += amount

    def level_up(self):
        xp_required = 50 * self.level
        if self.xp >= xp_required:
            self.xp -= xp_required
            self.level += 1
            self.attack += 5
            self.max_health += 10  # Increase max health on level up
            self.health = self.max_health  # Restore health to max health
            print(f"You leveled up to level {self.level}! Your attack has increased by {self.attack} and your health is now {self.health}.")
        print(self.xp_progress_bar())

    def xp_progress_bar(self):
        xp_required = 50 * self.level
        progress = int((self.xp / xp_required) * 20)  # 20 is the length of the progress bar
        return f"XP Progress: [{'█' * progress}{'░' * (20 - progress)}] {self.xp}/{xp_required}"

    def use_skill(self, skill_name, monster):
        skill = self.skills.get(skill_name)
        if skill and random.random() < skill["chance"]:
            if "damage" in skill:
                print(f"You used {skill_name} and dealt {skill['damage']} damage with a {skill['chance']*100}% chance!")
                if "debuff" in skill:
                    monster.buff_debuff_manager.add_debuff(skill["debuff"]["type"], skill["debuff"]["amount"], skill["debuff"]["duration"])
                return skill["damage"]
            elif "heal" in skill:
                self.health = min(self.max_health, self.health + skill["heal"])  # Ensure health does not exceed max health
                print(f"You used {skill_name} and healed for {skill['heal']} health with a {skill['chance']*100}% chance!")
                return 0
        return 0

    def apply_debuffs(self):
        self.buff_debuff_manager.apply_debuffs(self)

    def apply_buffs(self, in_battle=False):
        self.buff_debuff_manager.apply_buffs(self, in_battle)

    def use_potion(self, potion_name):
        for i, (name, amount, tipe) in enumerate(self.inventory_potions):
            if name == potion_name:
                if tipe == "health":
                    self.health = min(self.max_health, self.health + amount)  # Ensure health does not exceed max health
                    print(f"You used a {potion_name} and recovered {amount} health points.")
                elif tipe == "attack":
                    self.buff_debuff_manager.add_buff("Attack Up", amount, 1)
                    print(f"You used a {potion_name} and increased your attack by {amount} for this battle.")
                elif tipe == "defense":
                    self.buff_debuff_manager.add_buff("Defense Up", amount, 1)
                    print(f"You used a {potion_name} and increased your defense by {amount} for this battle.")
                elif tipe == "crit":
                    self.buff_debuff_manager.add_battle_buff("Crit Up", amount, amount)
                    print(f"You used a {potion_name} and increased your critical hit chance and damage by {amount} for this battle.")
                del self.inventory_potions[i]
                break

    def clear_battle_buffs(self):
        self.buff_debuff_manager.clear_battle_buffs(self)

    def equip_item(self, item_name):
        for i, (name, amount, tipe, stats) in enumerate(self.inventory_items):
            if name == item_name:
                if tipe == "accessory":
                    if len(self.equipped_accessories) >= 3:
                        print("You can only equip up to 3 accessories.")
                        return
                    self.equipped_accessories.append((name, amount, stats))
                else:
                    if tipe in self.equipped_items:
                        print(f"You already have a {tipe} item equipped. Unequip it first.")
                        return
                    self.equipped_items[tipe] = (name, amount)
                if stats == "attack":
                    self.attack += amount
                    print(f"Your attack is now {self.attack}.")
                elif stats == "defense":
                    self.defense += amount
                    print(f"Your defense is now {self.defense}.")
                elif stats == "crit":
                    self.base_crit_chance += amount
                    self.base_crit_damage += amount
                    print(f"Your crit is now {self.base_crit_chance * 100}% critical chance and {self.base_crit_damage}x critical damage.")
                elif stats == "speed":
                    self.speed += amount
                    print(f"Your speed is now {self.speed}.")
                del self.inventory_items[i]
                print(f"You equipped {item_name}.")
                return
        print(f"{item_name} is not in your inventory.")

    def unequip_item(self, tipe):
        if tipe == "accessory":
            if self.equipped_accessories:
                print("Equipped accessories:")
                for i, (name, amount, stats) in enumerate(self.equipped_accessories, 1):
                    print(f"{i}. {name} ({amount} {stats} points)")
                accessory_choice = int(input("Enter the number of the accessory you want to unequip: ")) - 1
                if 0 <= accessory_choice < len(self.equipped_accessories):
                    name, amount, stats = self.equipped_accessories.pop(accessory_choice)
                    if stats == "attack":
                        self.attack -= amount
                        print(f"Your attack is now {self.attack}.")
                    elif stats == "defense":
                        self.defense -= amount
                        print(f"Your defense is now {self.defense}.")
                    elif stats == "crit":
                        self.base_crit_chance -= amount
                        self.base_crit_damage -= amount
                        print(f"Your crit is now {self.base_crit_chance} critical chance and {self.base_crit_damage}x critical damage.")
                    elif stats == "speed":
                        self.speed -= amount
                        print(f"Your speed is now {self.speed}.")
                        self.inventory_items.append((name, amount, "accessory", stats))
                    print(f"You unequipped {name}.")
                else:
                    print("Invalid choice.")
            else:
                print("You don't have any accessories equipped.")
        else:
            if tipe in self.equipped_items:
                name, amount, stats = self.equipped_items.pop(tipe)
                if stats == "attack":
                    self.attack -= amount
                    print(f"Your attack is now {self.attack}.")
                elif stats == "defense":
                    self.defense -= amount
                    print(f"Your defense is now {self.defense}.")
                self.inventory_items.append((name, amount, tipe, stats))
                print(f"You unequipped {name}.")
            else:
                print(f"You don't have a {tipe} item equipped.")

    def display_inventory(self):
        if self.inventory_items:
            items = [f"{name} ({amount} {stats} points)" for name, amount, tipe, stats in self.inventory_items]
            print(f"Equipment: {', '.join(items)}")
        else:
            print("Equipment: nothing")
        if self.inventory_potions:
            potions = [f"{name} ({amount} {tipe} points)" for name, amount, tipe in self.inventory_potions]
            print(f"Inventory: {', '.join(potions)}")
        else:
            print("Inventory: nothing")

    def display_equipped_items(self):
        if self.equipped_items or self.equipped_accessories:
            print("Items currently equipped:")
            for tipe, (name, amount, stats) in self.equipped_items.items():
                print(f"{tipe}: {name} ({amount} points)")
            for i, (name, amount, stats) in enumerate(self.equipped_accessories, 1):
                print(f"Accessory {i}: {name} ({amount} {stats} points)")
        else:
            print("You have no items equipped.")

class Monster:
    def __init__(self, name, defense, health, attack, xpdropmin, xpdropmax, min_gold, max_gold, skills):
        self.name = name
        self.defense = defense
        self.health = health
        self.attack = attack
        self.xpdropmin = xpdropmin
        self.xpdropmax = xpdropmax
        self.min_gold = min_gold
        self.max_gold = max_gold
        self.skills = skills
        self.buff_debuff_manager = BuffDebuffManager()

    def take_damage(self, total_damage):
        self.health -= total_damage

    def is_alive(self):
        return self.health > 0
    
    def use_skill(self, player):
        for skill_name, skill in self.skills.items():
            if random.random() < skill["chance"]:
                if "damage" in skill:
                    if "debuff" in skill:
                        damage = skill["debuff"].get("damage", 0)
                        player.buff_debuff_manager.add_debuff(skill["debuff"]["type"], damage, skill["debuff"]["duration"])
                    return skill["damage"], skill_name
                elif "heal" in skill:
                    self.health += skill["heal"]
                    return 0, skill_name
        return 0, None

    def apply_buffs(self):
        self.buff_debuff_manager.apply_buffs(self)
    
    def apply_debuffs(self):
        self.buff_debuff_manager.apply_debuffs(self)

class Shop:
    def __init__(self, items, potions):
        self.potions = potions
        self.items = items

    def display_items(self, player):
        print("Welcome to the Shop!")
        print(f"You have {player.gold} gold")
        for i, (item, price, amount, tipe, stats) in enumerate(self.items, 1):
            print(f"{i}. {item} ({tipe}) - {price} gold add {amount} of {stats} points")

    def display_potions(self, player):
        print("Welcome to the Shop!")
        print(f"You have {player.gold} gold")
        for i, (potion, price, amount, tipe) in enumerate(self.potions, 1):
            print(f"{i}. {potion} - {price} gold add {amount} of {tipe} points") 

    def buy_potion(self, player, potion_number):
        if 1 <= potion_number <= len(self.potions):
            potion_name, price, amount, tipe = self.potions[potion_number - 1]
            if player.gold >= price:
                player.gold -= price
                player.inventory_potions.append((potion_name, amount, tipe))
                print(f"You bought a {potion_name} for {price} gold.")
            else:
                print("You don't have enough gold to buy this potion.")
        else:
            print("Invalid potion number.")

    def buy_item(self, player, item_number):
        if 1 <= item_number <= len(self.items):
            item_name, price, amount, tipe, stats = self.items[item_number - 1]
            if player.gold >= price:
                player.gold -= price
                player.inventory_items.append((item_name, amount, tipe, stats))
                print(f"You bought a {item_name} for {price} gold.")
                # Remove the item from the shop's inventory
                self.items.pop(item_number - 1)
            else:
                print("You don't have enough gold to buy this item.")
        else:
            print("Invalid item number.")
            
class Dungeon:
    def __init__(self):
        self.current_floor = 1

    def get_monster(self):
        base_monster = self.choose_monster()
        multiplier = 1 + (self.current_floor - 1) * 0.1  # Increase stats by 10% per floor
        return Monster(
            base_monster["name"],
            int(base_monster["defense"] * multiplier),
            int(base_monster["health"] * multiplier),
            int(base_monster["attack"] * multiplier),
            int(base_monster["xpdropmin"] * multiplier),
            int(base_monster["xpdropmax"] * multiplier),
            int(base_monster["min_gold"] * multiplier),
            int(base_monster["max_gold"] * multiplier),
            base_monster["skills"]
        )

    def choose_monster(self):
        total_chance = sum(monster["chance"] for monster in monsters)
        pick = random.uniform(0, total_chance)
        current = 0
        for monster in monsters:
            current += monster["chance"]
            if current > pick:
                return monster

    def next_floor(self, player):
        self.current_floor += 1
        print(f"You have reached floor {self.current_floor}.")
        if self.current_floor % 5 == 0:
            print("You have the option to rest and recover health.")
            print("1. Rest")
            print("2. Continue")
            choice = input("Enter your choice: ")
            if choice == "1":
                if random.random() < 0.3:
                    health_loss = round(random.randint(5, 25) / 100 * player.health)
                    player.health -= health_loss
                    print(f"You were attacked while resting and lost {health_loss:.2f} health points!")
                else:
                    health_recovery = round(random.randint(5, 25) / 100 * player.health)
                    player.health += health_recovery
                    print(f"You have recovered {health_recovery:.2f} health points!")

class BuffDebuffManager:
    def __init__(self):
        self.buffs = {}
        self.debuffs = {}
        self.battle_buffs = {}

    def apply_buffs(self, target, in_battle=False):
        for buff, effect in list(self.buffs.items()):
            if effect["duration"] > 0:
                if buff == "Attack Up":
                    target.attack += effect["amount"]
                    print(f"{target.name}'s attack is increased by {effect['amount']}. {effect['duration']} turns remaining.")
                elif buff == "Defense Up":
                    target.defense += effect["amount"]
                    print(f"{target.name}'s defense is increased by {effect['amount']}. {effect['duration']} turns remaining.")
                if in_battle:
                    effect["duration"] -= 1
                    print(f"{buff} effect will last for {effect['duration']} more turns.")
            else:
                if buff == "Attack Up":
                    target.attack -= effect["amount"]
                    print(f"{target.name}'s attack is restored by {effect['amount']}.")
                elif buff == "Defense Up":
                    target.defense -= effect["amount"]
                    print(f"{target.name}'s defense is restored by {effect['amount']}.")
                del self.buffs[buff]

    def apply_debuffs(self, target):
        for debuff, effect in list(self.debuffs.items()):
            if effect["duration"] > 0:
                if debuff == "Poison":
                    target.health -= effect["damage"]
                    print(f"{target.name} takes {effect['damage']} poison damage. {effect['duration']} turns remaining.")
                elif debuff == "Defense Down":
                    target.defense = max(0, target.defense - effect["amount"])
                    print(f"{target.name}'s defense is decreased by {effect['amount']}. {effect['duration']} turns remaining.")
                elif debuff == "Bleed":
                    target.health -= effect["damage"]
                    print(f"{target.name} takes {effect['damage']} bleeding damage. {effect['duration']} turns remaining.")
                elif debuff == "Stun":
                    print(f"{target.name} is stunned and cannot move for {effect['duration']} turns.")
                elif debuff == "Burn":
                    target.health -= effect["damage"]
                    print(f"{target.name} takes {effect['damage']} burn damage. {effect['duration']} turns remaining.")
                effect["duration"] -= 1
            else:
                if debuff == "Defense Down":
                    target.defense += effect["amount"]
                    print(f"{target.name}'s defense is restored by {effect['amount']}.")
                del self.debuffs[debuff]

    def add_buff(self, buff, amount, duration):
        self.buffs[buff] = {"amount": amount, "duration": duration}

    def add_debuff(self, debuff, damage, duration):
        self.debuffs[debuff] = {"damage": damage, "duration": duration}

    def add_battle_buff(self, buff, crit_chance, crit_damage):
        self.battle_buffs[buff] = {"crit_chance": crit_chance, "crit_damage": crit_damage}

    def clear_battle_buffs(self, target):
        for buff, effect in self.battle_buffs.items():
            if buff == "Crit Up":
                target.base_crit_chance -= effect["crit_chance"]
                target.base_crit_damage -= effect["crit_damage"]
                print(f"{target.name}'s critical hit chance and damage are restored by {effect['crit_chance']} and {effect['crit_damage']}.")
        self.battle_buffs.clear()

def battle(player, monster, dungeon):
    while player.is_alive() and monster.is_alive():
        player.apply_debuffs()
        player.apply_buffs(in_battle=True)
        monster.apply_debuffs()
        monster.apply_buffs()
        print(f"{player.name}'s health: {player.health}")
        print(f"{monster.name}'s health: {monster.health}")
        
        if "Stun" in player.buff_debuff_manager.debuffs and player.buff_debuff_manager.debuffs["Stun"]["duration"] > 0:
            print("You are stunned and cannot move this turn.")
            player.buff_debuff_manager.debuffs["Stun"]["duration"] -= 1
        else:
            player_action(player, monster)

        if monster.is_alive():
            monster_action(monster, player)

    handle_battle_end(player, monster, dungeon)

def player_action(player, monster):
    print("\nWhat will you do?")
    print("1. Attack")
    print("2. Use Skill")
    print("3. Use Potion")
    print("4. Run")
    choice = input("Enter your choice: ")

    if choice == '1':
        player_attack(player, monster)
    elif choice == '2':
        player_use_skill(player, monster)
    elif choice == '3':
        player_use_potion(player)
    elif choice == '4':
        if player_run_away(player):
            return
    else:
        print("Invalid choice. Try again.")

def player_attack(player, monster):
    player.step_count += 1
    crit_chance = player.base_crit_chance + player.buff_debuff_manager.battle_buffs.get("Crit Up", {}).get("crit_chance", 0)
    crit_damage = player.base_crit_damage + player.buff_debuff_manager.battle_buffs.get("Crit Up", {}).get("crit_damage", 0)
    if random.random() < crit_chance:
        damage = random.randint(0, player.attack) * crit_damage
        absorb = random.randint(0, max(0, monster.defense))
        total_damage = max(0, damage - absorb)
        print(f"Critical hit! You hit the {monster.name} for {total_damage} damage!")
    else:
        damage = random.randint(0, player.attack)
        absorb = random.randint(0, max(0, monster.defense))
        total_damage = max(0, damage - absorb)
        print(f"You hit the {monster.name} for {total_damage} damage!")
    monster.take_damage(total_damage)

def player_use_skill(player, monster):
    player.step_count += 1
    print("Skills available:")
    skill_list = list(player.skills.keys())
    for i, skill_name in enumerate(skill_list, 1):
        skill = player.skills[skill_name]
        print(f"{i}. {skill_name} - {skill['chance']*100}% chance to deal {skill.get('damage', 0)} damage")
    skill_choice = int(input("Enter the number of the skill you want to use: ")) - 1
    if 0 <= skill_choice < len(skill_list):
        skill_name = skill_list[skill_choice]
        damage = player.use_skill(skill_name, monster) 
        total_damage = max(0, damage - random.randint(0, max(0, monster.defense)))
        if total_damage > 0:
            print(f"You used {skill_name} and dealt {total_damage} damage to the {monster.name}!")
            monster.take_damage(total_damage)
        else:
            print(f"You used {skill_name} but missed!")
    else:
        print("Invalid skill choice.")

def player_use_potion(player):
    if player.inventory_potions:
        print("Potions available:")
        for i, item in enumerate(player.inventory_potions, 1):
            if len(item) == 3:  # Ensure it's a potion
                name, amount, tipe = item
                print(f"{i}. {name} - {amount} {tipe} points")
        potion_choice = int(input("Enter the number of the potion you want to use: ")) - 1
        if 0 <= potion_choice < len(player.inventory_potions):
            potion_name = player.inventory_potions[potion_choice][0]
            player.use_potion(potion_name)
        else:
            print("Invalid choice.")
    else:
        print("You have no potions in your inventory.")

def player_run_away(player):
    player.step_count += 1
    if random.random() < 0.3:
        print("You run away from the battle. Coward!")
        return True
    else:
        print("You tried to run away but the monster caught you!")
        return False

def monster_action(monster, player):
    damage, skill_name = monster.use_skill(player)
    if skill_name:
        if damage > 0:
            print(f"The {monster.name} used {skill_name} and dealt {damage} damage to you!")
            player.take_damage(damage)
        else:
            print(f"The {monster.name} used {skill_name} and healed itself!")
    else:
        damage = random.randint(0, monster.attack)
        print(f"The {monster.name} attacks you for {damage} damage!")
        player.take_damage(damage)

def handle_battle_end(player, monster, dungeon):
    if player.is_alive() and not monster.is_alive():
        xp_earned = random.randint(monster.xpdropmin, monster.xpdropmax)
        gold_earned = random.randint(monster.min_gold, monster.max_gold)
        player.earn_gold(gold_earned)
        player.earn_xp(xp_earned)
        print(f"You defeated the {monster.name} and earned {xp_earned} XP and found {gold_earned} Golds!")
        player.level_up()
            
        # Drop items
        if random.random() < 1:  # 10% chance to drop an item
            dropped_item = random.choice(item_drops)
            item_names = [item[0] for item in player.inventory_items]
            if dropped_item[0] not in item_names:
                player.inventory_items.append(dropped_item)
                print(f"The {monster.name} dropped a {dropped_item[0]} ({dropped_item[2]} {dropped_item[3]} points)!")
            else:
                print(f"The {monster.name} dropped a {dropped_item[0]}, but you already have it.")

    elif not player.is_alive():
        print("You were defeated by the monster!")
        player.health = 100
        player.gold = 0
        player.xp = 0
        player.level = 1
        player.attack = 20
        player.inventory_items = []
        player.inventory_potions = []
        player.step_count = 0
        player.debuffs = {}
        dungeon.current_floor = 0

    # Clear battle buffs after the battle ends
    player.clear_battle_buffs()

# Define monsters
monsters = [
    {"name": "Goblin", "defense": 5, "health": 50, "attack": 10, "xpdropmin": 5, "xpdropmax": 10, "min_gold": 5, "max_gold": 10, "skills": {"Poison": {"damage": 5, "chance": 0.2, "debuff": {"type": "Poison", "damage": 2, "duration": 3}}}, "chance": 0.2},
    {"name": "Kobold", "defense": 5, "health": 40, "attack": 8, "xpdropmin": 4, "xpdropmax": 8, "min_gold": 4, "max_gold": 8, "skills": {"Stab": {"damage": 4, "chance": 0.3, "debuff": {"type": "Bleed", "damage": 3, "duration": 2}}}, "chance": 0.2},
    {"name": "Orc", "defense": 10, "health": 100, "attack": 20, "xpdropmin": 10, "xpdropmax": 15, "min_gold": 10, "max_gold": 20, "skills": {"Smash": {"damage": 10, "chance": 0.15, "debuff": {"type": "Stun", "duration": 2}}}, "chance": 0.15},
    {"name": "Troll", "defense": 10, "health": 150, "attack": 25, "xpdropmin": 15, "xpdropmax": 20, "min_gold": 15, "max_gold": 25, "skills": {"Regenerate": {"heal": 10, "chance": 0.1, "buff": {"type": "Defense Up", "amount": 3, "duration": 2}}}, "chance": 0.1},
    {"name": "Minotaur", "defense": 20, "health": 200, "attack": 30, "xpdropmin": 20, "xpdropmax": 25, "min_gold": 20, "max_gold": 30, "skills": {"Charge": {"damage": 20, "chance": 0.2}}, "chance": 0.1},
    {"name": "Giant", "defense": 25, "health": 250, "attack": 35, "xpdropmin": 25, "xpdropmax": 30, "min_gold": 25, "max_gold": 35, "skills": {"Stomp": {"damage": 25, "chance": 0.15}}, "chance": 0.1},
    {"name": "Dragon", "defense": 30, "health": 500, "attack": 50, "xpdropmin": 30, "xpdropmax": 40, "min_gold": 30, "max_gold": 50, "skills": {"Fire Breath": {"damage": 30, "chance": 0.1}}, "chance": 0.095},
    {"name": "Hydra", "defense": 30, "health": 450, "attack": 45, "xpdropmin": 25, "xpdropmax": 35, "min_gold": 25, "max_gold": 45, "skills": {"Regenerate": {"heal": 20, "chance": 0.2}}, "chance": 0.095},
    {"name": "Demon Lord", "defense": 40, "health": 1000, "attack": 60, "xpdropmin": 50, "xpdropmax": 60, "min_gold": 50, "max_gold": 60, "skills": {"Dark Flame": {"damage": 50, "chance": 0.2}}, "chance": 0.01}
]

if __name__ == "__main__":
    print("Welcome to the Text RPG Game!")
    player_name = input("Enter your character's name: ")
    
    classes = ["Warrior", "Mage", "Rogue"]
    classes.sort()
    
    print("Choose your class:")
    for i, player_class in enumerate(classes, 1):
        print(f"{i}. {player_class}")
    class_choice = input("Enter the number of your class: ")
    
    try:
        player_class = classes[int(class_choice) - 1]
    except (IndexError, ValueError):
        print("Invalid choice. Defaulting to Warrior.")
        player_class = "Warrior"
    
    player = Player(player_name, player_class)

    item_drops = [
    ("Ring of Strength", 5, "accessory", "attack"),
    ("Weak finder", 0.1, "accessory", "crit"),
    ("Amulet of Protection", 5, "accessory", "defense")
    ]
    
    shop_items = [
        ("Sword", 50, 15, "primary", "attack"),
        ("Dagger", 30, 10, "primary", "attack"),
        ("Shield", 30, 10, "secondary", "defense"),
        ("Helmet", 20, 5, "helmet", "defense"),
        ("Armor", 40, 20, "armor", "defense")
    ]

    shop_potions = [
        ("Health Potion", 10, 20, "health"),
        ("Strength Potion", 20, 10, "attack"),
        ("Stone Potion", 10, 20, "defense"),
        ("Critical Potion", 15, 0.1, "crit")  # Increase crit chance and damage by 0.1
    ]
    shop = Shop(shop_items, shop_potions)
    dungeon = Dungeon()

    while True:
        print(f"\nSteps taken: {player.step_count}")
        print(f"Current Floor: {dungeon.current_floor}")
        print("\nMain Menu:")
        print("1. Battle a Monster")
        print("2. Visit the Shop")
        print("3. View Stats")
        print("4. Equip/Unequip Items")
        print("5. Quit")
        choice = input("Enter your choice: ")

        if choice == "1":
            player.step_count += 1
            monster = dungeon.get_monster()
            print(f"A wild {monster.name} appears!\n")
            battle(player, monster, dungeon)
            if player.is_alive():
                dungeon.next_floor(player)
        elif choice == '2':
            print("1. Equipment")
            print("2. Consumables/Potions")
            sub_choice = input("Enter your choice: ")
            if sub_choice == '1':
                shop.display_items(player)
                item_number = input("Enter the number of the item you want to buy or 'q' to quit: ")
                if item_number == 'q':
                    continue
                shop.buy_item(player, int(item_number))
            elif sub_choice == '2':
                shop.display_potions(player)
                potion_number = input("Enter the number of the potion you want to buy or 'q' to quit: ")
                if potion_number == 'q':
                    continue
                shop.buy_potion(player, int(potion_number))
        elif choice == '3':
            print(f"Name: {player.name}")
            print(f"Class: {player.player_class}")
            print(f"Level: {player.level}")
            print(f"Health: {player.health}")
            print(f"Attack: {player.attack}")
            print(f"Defense: {player.defense}")
            print(f"Skills: {', '.join(player.skills.keys())}")
            print(f"Passive: {player.passive}")
            print(player.xp_progress_bar())
            player.display_inventory()
            print(f"XP: {player.xp}")
            print(f"Gold: {player.gold}")
            print(f"Steps taken: {player.step_count}")
        elif choice == '4':
            print("1. Equip Item")
            print("2. Unequip Item")
            equip_choice = input("Enter your choice: ")
            if equip_choice == '1':
                if player.inventory_items:
                    print("Items available to equip:")
                    for i, (name, amount, tipe, stats) in enumerate(player.inventory_items, 1):
                        print(f"{i}. {name} ({amount} {stats} points)")
                    item_choice = int(input("Enter the number of the item you want to equip: ")) - 1
                    if 0 <= item_choice < len(player.inventory_items):
                        item_name = player.inventory_items[item_choice][0]
                        player.equip_item(item_name)
                    else:
                        print("Invalid choice.")
                else:
                    print("You have no items in your inventory.")
            elif equip_choice == '2':
                if player.equipped_items:
                    print("Items currently equipped:")
                    for tipe, (name, amount, stats) in player.equipped_items.items():
                        print(f"{tipe}: {name} ({amount} points)")
                    tipe_choice = input("Enter the type of item you want to unequip (primary/secondary/helmet/armor): ")
                    player.unequip_item(tipe_choice)
                else:
                    print("You have no items equipped.")
        elif choice == '5':
            print("Thanks for playing! Goodbye.")
            break
        else:
            print("Invalid choice. Try again.")