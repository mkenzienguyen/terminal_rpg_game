import random
import time
import sys
from weapons import Weapon, WeaponManager
from save_profiles import SaveManager, display_save_info


class Character:
    """Base character class with stats and health"""
    
    def __init__(self, name, health=100, attack=10, defense=5):
        self.name = name
        self.max_health = health
        self.health = health
        self.base_attack = attack
        self.attack = attack
        self.defense = defense
        self.position = [0, 0]  # x, y coordinates
        self.inventory = []
        self.level = 1
        self.experience = 0
        self.equipped_weapon = None
        self.gold = 100  # Starting gold
        
    def equip_weapon(self, weapon):
        """Equip a weapon"""
        if self.equipped_weapon:
            print(f"\n  Unequipped: {self.equipped_weapon.name}")
        
        self.equipped_weapon = weapon
        self.attack = self.base_attack + weapon.attack
        print(f"\n  ⚔️  Equipped: {weapon.name}")
        print(f"  Attack power increased to {self.attack}!")
    
    def unequip_weapon(self):
        """Remove equipped weapon"""
        if self.equipped_weapon:
            weapon = self.equipped_weapon
            self.equipped_weapon = None
            self.attack = self.base_attack
            print(f"\n  Unequipped: {weapon.name}")
            return weapon
        return None
        
    def is_alive(self):
        return self.health > 0
    
    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense)
        self.health -= actual_damage
        self.health = max(0, self.health)
        return actual_damage
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def attack_target(self, target):
        damage = random.randint(int(self.attack - 2), int(self.attack + 5))
        
        # Check weapon durability
        if self.equipped_weapon:
            broke = self.equipped_weapon.use()
            if broke:
                print(f"\n  💔 {self.equipped_weapon.name} broke!")
                self.equipped_weapon = None
                self.attack = self.base_attack
        
        return target.take_damage(damage)
    
    def display_stats(self):
        print(f"\n{'='*40}")
        print(f"  {self.name} - Level {self.level}")
        print(f"{'='*40}")
        print(f"  Health: {self.health}/{self.max_health}")
        print(f"  Base Attack: {self.base_attack}")
        if self.equipped_weapon:
            print(f"  Equipped: {self.equipped_weapon.name} (+{self.equipped_weapon.attack})")
            durability_str = "∞" if self.equipped_weapon.max_durability == 0 else f"{self.equipped_weapon.durability}/{self.equipped_weapon.max_durability}"
            print(f"  Weapon Durability: {durability_str}")
        print(f"  Total Attack: {self.attack}")
        print(f"  Defense: {self.defense}")
        print(f"  Gold: {self.gold}")
        print(f"  Position: ({self.position[0]}, {self.position[1]})")
        print(f"  XP: {self.experience}")
        if self.inventory:
            print(f"  Inventory ({len(self.inventory)} items):")
            for item in self.inventory:
                if isinstance(item, Weapon):
                    print(f"    • {item.get_rarity_color()} {item.name} (ATK: {item.attack})")
                else:
                    print(f"    • {item}")
        print(f"{'='*40}\n")
    
    def gain_experience(self, xp):
        self.experience += xp
        print(f"\n{self.name} gained {xp} experience!")
        
        # Level up every 100 XP
        while self.experience >= 100:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.experience -= 100
        self.max_health += 20
        self.health = self.max_health
        self.base_attack += 3
        self.attack = self.base_attack
        if self.equipped_weapon:
            self.attack += self.equipped_weapon.attack
        self.defense += 2
        
        print(f"\n🎉 LEVEL UP! {self.name} is now level {self.level}!")
        print(f"   Health: {self.max_health}")
        print(f"   Base Attack: {self.base_attack}")
        print(f"   Defense: {self.defense}\n")
        time.sleep(1)
    
    def add_gold(self, amount):
        self.gold += amount
        print(f"\n💰 Gained {amount} gold! (Total: {self.gold})")


class Enemy(Character):
    """Enemy character with specific behaviors"""
    
    def __init__(self, name, health, attack, defense, xp_reward, gold_reward):
        super().__init__(name, health, attack, defense)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward


class GameWorld:
    """Manages the game world, movement, and encounters"""
    
    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height
        self.player = None
        self.discovered = set()  # Track discovered locations
        self.enemies_at = {}  # Track enemy locations
        self.treasures_at = {}  # Track treasure locations
        self.weapon_manager = WeaponManager('weapons.txt')
        
    def move_character(self, character, direction):
        """Move character in a direction (up, down, left, right)"""
        moves = {
            'up': [0, 1],
            'down': [0, -1],
            'left': [-1, 0],
            'right': [1, 0]
        }
        
        if direction in moves:
            new_x = character.position[0] + moves[direction][0]
            new_y = character.position[1] + moves[direction][1]
            
            # Check boundaries
            if 0 <= new_x < self.width and 0 <= new_y < self.height:
                character.position = [new_x, new_y]
                # Mark as discovered
                self.discovered.add(tuple(character.position))
                print(f"\n{character.name} moved {direction} to ({new_x}, {new_y})")
                self.display_map()
                return True
            else:
                print("\n⚠️  Can't move there - you've hit the edge of the world!")
                return False
        return False
    
    def display_map(self):
        """Display the game world map with player position"""
        print("\n" + "═" * (self.width * 4 + 3))
        print("  " + " " * ((self.width * 4 - 7) // 2) + "WORLD MAP")
        print("═" * (self.width * 4 + 3))
        
        # Display from top to bottom (y from high to low)
        for y in range(self.height - 1, -1, -1):
            row = f"{y} ║"
            for x in range(self.width):
                pos = [x, y]
                
                # Check what to display at this position
                if pos == self.player.position:
                    cell = " 🧙"  # Player
                elif tuple(pos) in self.discovered:
                    cell = " · "  # Discovered empty space
                elif tuple(pos) in self.enemies_at:
                    cell = " 👹"  # Enemy location
                elif tuple(pos) in self.treasures_at:
                    cell = " 💎"  # Treasure location
                else:
                    cell = " ? "  # Undiscovered
                
                row += cell + " "
            
            row += "║"
            print(row)
        
        # Bottom border with x-axis labels
        print("  ╚" + "═" * (self.width * 4) + "╝")
        x_labels = "    "
        for x in range(self.width):
            x_labels += f"{x}   "
        print(x_labels)
        
        # Legend
        print("\n  Legend: 🧙=You  ·=Explored  ?=Unknown  👹=Enemy  💎=Treasure")
        print()
    
    def random_encounter(self):
        """Generate a random enemy encounter"""
        enemy_types = [
            ("Goblin", 30, 8, 2, 25, 15),
            ("Skeleton", 40, 10, 3, 35, 25),
            ("Orc", 60, 15, 5, 50, 40),
            ("Dark Knight", 80, 20, 8, 75, 60),
            ("Dragon", 150, 30, 12, 150, 100)
        ]
        
        # Difficulty scales with player level
        max_index = min(len(enemy_types) - 1, self.player.level)
        enemy_data = random.choice(enemy_types[:max_index + 1])
        
        return Enemy(*enemy_data)
    
    def find_treasure(self):
        """Random treasure finding"""
        treasure_roll = random.random()
        
        if treasure_roll < 0.3:  # 30% chance for weapon
            weapon = self.weapon_manager.get_weighted_random_weapon()
            if weapon:
                self.player.inventory.append(weapon)
                print(f"\n⚔️  You found a weapon: {weapon.get_rarity_color()} {weapon.name}!")
                print(f"   Attack: {weapon.attack} | {weapon.special_effect}")
        
        elif treasure_roll < 0.6:  # 30% chance for gold
            gold_amount = random.randint(20, 100)
            self.player.add_gold(gold_amount)
        
        else:  # 40% chance for potion
            self.player.heal(30)
            print(f"\n💊 You found a Potion! Healed for 30 HP!")


def shop_menu(player, weapon_manager):
    """Weapon shop for buying weapons"""
    print("\n" + "="*60)
    print("  🏪 WEAPON SHOP")
    print("="*60)
    print(f"  Your Gold: {player.gold}")
    print("="*60)
    
    # Show affordable weapons
    affordable = weapon_manager.get_affordable_weapons(player.gold)
    
    if not affordable:
        print("\n  You can't afford any weapons right now!")
        input("\n  Press Enter to leave the shop...")
        return
    
    # Group by rarity
    rarities = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
    shown_weapons = []
    
    for rarity in rarities:
        rarity_weapons = [w for w in affordable if w.rarity == rarity]
        if rarity_weapons:
            print(f"\n  {rarity.upper()}:")
            for weapon in rarity_weapons[:5]:  # Show max 5 per rarity
                shown_weapons.append(weapon)
                idx = len(shown_weapons)
                print(f"  {idx}. {weapon.get_rarity_color()} {weapon.name:20} - "
                      f"ATK: {weapon.attack:4.1f} | Cost: {weapon.cost} gold")
    
    print(f"\n  {len(shown_weapons) + 1}. Leave shop")
    
    try:
        choice = int(input("\n  Enter your choice: "))
        
        if 1 <= choice <= len(shown_weapons):
            weapon = shown_weapons[choice - 1]
            confirm = input(f"\n  Buy {weapon.name} for {weapon.cost} gold? (yes/no): ")
            
            if confirm.lower() in ['yes', 'y']:
                player.gold -= weapon.cost
                player.inventory.append(weapon)
                print(f"\n  ✅ Purchased {weapon.name}!")
                print(f"  Remaining gold: {player.gold}")
        
    except (ValueError, IndexError):
        print("\n  Invalid choice!")
    
    input("\n  Press Enter to continue...")


def inventory_menu(player):
    """Manage player inventory - view and equip weapons"""
    while True:
        print("\n" + "="*60)
        print("  🎒 INVENTORY")
        print("="*60)
        
        if player.equipped_weapon:
            print(f"\n  Currently Equipped: {player.equipped_weapon.get_rarity_color()} {player.equipped_weapon.name}")
            print(f"  Attack: {player.equipped_weapon.attack} | Durability: ", end="")
            if player.equipped_weapon.max_durability == 0:
                print("∞")
            else:
                print(f"{player.equipped_weapon.durability}/{player.equipped_weapon.max_durability}")
        else:
            print("\n  No weapon equipped (Using fists)")
        
        print(f"\n  Weapons in inventory:")
        weapons = [item for item in player.inventory if isinstance(item, Weapon)]
        
        if not weapons:
            print("  (Empty)")
        else:
            for idx, weapon in enumerate(weapons, 1):
                durability_str = "∞" if weapon.max_durability == 0 else f"{weapon.durability}/{weapon.max_durability}"
                print(f"  {idx}. {weapon.get_rarity_color()} {weapon.name:20} - "
                      f"ATK: {weapon.attack:4.1f} | DUR: {durability_str}")
        
        print(f"\n  {len(weapons) + 1}. Unequip current weapon")
        print(f"  {len(weapons) + 2}. Back to game")
        
        try:
            choice = int(input("\n  Enter your choice: "))
            
            if 1 <= choice <= len(weapons):
                player.equip_weapon(weapons[choice - 1])
                input("\n  Press Enter to continue...")
            
            elif choice == len(weapons) + 1:
                player.unequip_weapon()
                input("\n  Press Enter to continue...")
            
            elif choice == len(weapons) + 2:
                break
        
        except (ValueError, IndexError):
            print("\n  Invalid choice!")
            time.sleep(1)


def battle(player, enemy):
    """Battle system - turn-based combat"""
    print(f"\n{'⚔️ '*20}")
    print(f"  A wild {enemy.name} appears!")
    print(f"{'⚔️ '*20}\n")
    time.sleep(1)
    
    turn = 1
    
    while player.is_alive() and enemy.is_alive():
        print(f"\n--- Turn {turn} ---")
        print(f"Your HP: {player.health}/{player.max_health} | {enemy.name} HP: {enemy.health}/{enemy.max_health}")
        
        # Player's turn
        print("\nYour turn!")
        print("1. Attack")
        print("2. Defend (restore 15 HP)")
        print("3. Run (25% chance)")
        
        choice = input("\nChoose your action: ").strip()
        
        if choice == '1':
            damage = player.attack_target(enemy)
            print(f"\n⚔️  You strike {enemy.name} for {damage} damage!")
            time.sleep(0.5)
            
        elif choice == '2':
            player.heal(15)
            print(f"\n🛡️  You defend and recover 15 HP! (Health: {player.health}/{player.max_health})")
            time.sleep(0.5)
            
        elif choice == '3':
            if random.random() < 0.25:
                print("\n💨 You successfully fled from battle!")
                return False
            else:
                print("\n❌ Failed to escape!")
                time.sleep(0.5)
        
        # Check if enemy is defeated
        if not enemy.is_alive():
            print(f"\n🎉 Victory! You defeated the {enemy.name}!")
            player.gain_experience(enemy.xp_reward)
            player.add_gold(enemy.gold_reward)
            return True
        
        # Enemy's turn
        print(f"\n{enemy.name}'s turn!")
        time.sleep(0.5)
        damage = enemy.attack_target(player)
        print(f"💥 {enemy.name} attacks you for {damage} damage!")
        time.sleep(0.5)
        
        # Check if player is defeated
        if not player.is_alive():
            print("\n💀 You have been defeated...")
            return False
        
        turn += 1
    
    return player.is_alive()


def print_slow(text, delay=0.03):
    """Print text with a typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def main():
    """Main game loop"""
    print("\n" + "="*50)
    print_slow("  🎮 WELCOME TO THE TERMINAL RPG ADVENTURE! 🎮")
    print("="*50 + "\n")
    
    time.sleep(0.5)
    
    # Create game world and save manager first
    world = GameWorld(width=10, height=10)
    save_manager = SaveManager()
    
    # Check if save file exists
    if save_manager.save_exists():
        print("\n📂 Found existing save file!")
        display_save_info()
        
        load_choice = input("\nDo you want to load your saved game? (yes/no): ").strip().lower()
        
        if load_choice in ['yes', 'y']:
            # Create temporary player to load into
            player = Character("Temp", health=100, attack=15, defense=5)
            world.player = player
            
            # Load the save
            moves_count = save_manager.load_game(player, world, world.weapon_manager)
            
            if moves_count is not None:
                print("\n✅ Game loaded successfully!")
                time.sleep(1)
            else:
                print("\n❌ Failed to load game. Starting new game...")
                player = None
        else:
            player = None
            # Ask if they want to delete old save
            delete = input("\nDelete old save file? (yes/no): ").strip().lower()
            if delete in ['yes', 'y']:
                save_manager.delete_save()
    else:
        player = None
        moves_count = 0
    
    # If no player was loaded, create new character
    if player is None:
        moves_count = 0
        name = input("\nEnter your hero's name: ").strip() or "Hero"
        player = Character(name, health=100, attack=15, defense=5)
        
        print(f"\nWelcome, {player.name}! Your adventure begins...\n")
        time.sleep(1)
        
        # Set up new game
        world.player = player
        world.discovered.add(tuple(player.position))
        
        # Give player a starting weapon
        starting_weapon = world.weapon_manager.get_weapon_by_name("Rusty Sword")
        if starting_weapon:
            player.inventory.append(starting_weapon)
            player.equip_weapon(starting_weapon)
        
        print("\n📍 You begin your journey at the center of the realm...")
        world.display_map()
        time.sleep(1)
    
    while player.is_alive():
        print("\n" + "-"*50)
        print("What would you like to do?")
        print("-"*50)
        print("1. View Stats")
        print("2. View Map")
        print("3. Move (up/down/left/right)")
        print("4. Explore (chance of battle or treasure)")
        print("5. Rest (heal 25 HP)")
        print("6. Inventory (manage weapons)")
        print("7. Shop (buy weapons)")
        print("8. Save Game")
        print("9. Quit")
        
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '1':
            player.display_stats()
            
        elif choice == '2':
            world.display_map()
            
        elif choice == '3':
            direction = input("Which direction? (up/down/left/right): ").strip().lower()
            if world.move_character(player, direction):
                moves_count += 1
                
                # Random encounter after moving
                if random.random() < 0.4:  # 40% chance
                    enemy = world.random_encounter()
                    battle_won = battle(player, enemy)
                    
                    if not player.is_alive():
                        break
                    
                    if battle_won and random.random() < 0.3:  # 30% chance after winning
                        world.find_treasure()
            
        elif choice == '4':
            print("\nYou explore the area...")
            time.sleep(1)
            
            if random.random() < 0.6:  # 60% chance of battle
                enemy = world.random_encounter()
                battle_won = battle(player, enemy)
                
                if not player.is_alive():
                    break
                    
                if battle_won and random.random() < 0.4:
                    world.find_treasure()
            else:
                print("\nYou find nothing of interest...")
                if random.random() < 0.5:
                    world.find_treasure()
        
        elif choice == '5':
            player.heal(25)
            print(f"\n😴 You rest and recover 25 HP. Current health: {player.health}/{player.max_health}")
        
        elif choice == '6':
            inventory_menu(player)
        
        elif choice == '7':
            shop_menu(player, world.weapon_manager)
        
        elif choice == '8':
            save_manager = SaveManager()
            save_manager.save_game(player, world, moves_count)
            input("\nPress Enter to continue...")
            
        elif choice == '9':
            print(f"\nThanks for playing! You reached level {player.level} with {len(player.inventory)} items.")
            print(f"Total moves: {moves_count}")
            break
        
        else:
            print("\n❌ Invalid choice. Please try again.")
    
    if not player.is_alive():
        print("\n" + "="*50)
        print("         💀 GAME OVER 💀")
        print("="*50)
        print(f"\n{player.name} fell in battle at level {player.level}.")
        print(f"Total moves: {moves_count}")
        print(f"Items collected: {len(player.inventory)}")
        print("\nBetter luck next time, adventurer!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)