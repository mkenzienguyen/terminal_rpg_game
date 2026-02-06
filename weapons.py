class Weapon:
    """Class representing a weapon"""
    
    def __init__(self, name, attack, rarity, durability, cost, weapon_type, special_effect, description):
        self.name = name
        self.attack = float(attack)
        self.rarity = rarity
        self.durability = int(durability)
        self.max_durability = int(durability)
        self.cost = int(cost)
        self.weapon_type = weapon_type
        self.special_effect = special_effect
        self.description = description
    
    def __str__(self):
        return f"{self.name} ({self.rarity})"
    
    def display_full_stats(self):
        """Display complete weapon information"""
        print(f"\n{'='*60}")
        print(f"  {self.name}")
        print(f"{'='*60}")
        print(f"  Type: {self.weapon_type}")
        print(f"  Rarity: {self.rarity}")
        print(f"  Attack Power: {self.attack}")
        print(f"  Durability: {self.durability}/{self.max_durability}" + 
              (" (Unbreakable)" if self.max_durability == 0 else ""))
        print(f"  Cost: {self.cost} gold")
        if self.special_effect != "None":
            print(f"  Special: {self.special_effect}")
        print(f"  \"{self.description}\"")
        print(f"{'='*60}\n")
    
    def use(self):
        """Use the weapon (decreases durability)"""
        if self.max_durability > 0:  # Only break if not infinite durability
            self.durability -= 1
            if self.durability <= 0:
                return True  # Weapon broke
        return False  # Weapon still good
    
    def repair(self, amount=None):
        """Repair the weapon"""
        if amount is None:
            self.durability = self.max_durability
        else:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def get_rarity_color(self):
        """Get color code for rarity (for display)"""
        colors = {
            'Common': '⚪',
            'Uncommon': '🟢',
            'Rare': '🔵',
            'Epic': '🟣',
            'Legendary': '🟡'
        }
        return colors.get(self.rarity, '⚪')


class WeaponManager:
    """Manages loading and accessing weapons from file"""
    
    def __init__(self, filename='weapons.txt'):
        self.weapons = []
        self.load_weapons(filename)
    
    def load_weapons(self, filename):
        """Load weapons from text file"""
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse weapon data
                    parts = line.split('|')
                    if len(parts) == 8:
                        weapon = Weapon(
                            name=parts[0].strip(),
                            attack=parts[1].strip(),
                            rarity=parts[2].strip(),
                            durability=parts[3].strip(),
                            cost=parts[4].strip(),
                            weapon_type=parts[5].strip(),
                            special_effect=parts[6].strip(),
                            description=parts[7].strip()
                        )
                        self.weapons.append(weapon)
            
            print(f"Loaded {len(self.weapons)} weapons from {filename}")
        
        except FileNotFoundError:
            print(f"Error: {filename} not found!")
        except Exception as e:
            print(f"Error loading weapons: {e}")
    
    def get_weapon_by_name(self, name):
        """Get a weapon by its name"""
        for weapon in self.weapons:
            if weapon.name.lower() == name.lower():
                return weapon
        return None
    
    def get_weapons_by_rarity(self, rarity):
        """Get all weapons of a specific rarity"""
        return [w for w in self.weapons if w.rarity == rarity]
    
    def get_weapons_by_type(self, weapon_type):
        """Get all weapons of a specific type"""
        return [w for w in self.weapons if w.weapon_type == weapon_type]
    
    def get_affordable_weapons(self, gold):
        """Get all weapons the player can afford"""
        return [w for w in self.weapons if w.cost <= gold]
    
    def list_all_weapons(self):
        """Display all weapons"""
        rarities = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
        
        for rarity in rarities:
            weapons = self.get_weapons_by_rarity(rarity)
            if weapons:
                print(f"\n{rarity.upper()} WEAPONS:")
                print("-" * 80)
                for weapon in weapons:
                    durability_str = "∞" if weapon.max_durability == 0 else str(weapon.max_durability)
                    print(f"{weapon.get_rarity_color()} {weapon.name:25} | "
                          f"ATK: {weapon.attack:4.1f} | "
                          f"DUR: {durability_str:3} | "
                          f"Cost: {weapon.cost:4} | "
                          f"{weapon.weapon_type:8} | "
                          f"{weapon.special_effect}")
    
    def get_random_weapon(self, rarity=None):
        """Get a random weapon, optionally filtered by rarity"""
        import random
        
        if rarity:
            available = self.get_weapons_by_rarity(rarity)
        else:
            available = self.weapons
        
        if available:
            return random.choice(available)
        return None
    
    def get_weighted_random_weapon(self):
        """Get a random weapon with rarity-based weighting"""
        import random
        
        # Weights: Common (50%), Uncommon (25%), Rare (15%), Epic (8%), Legendary (2%)
        rarity_weights = {
            'Common': 50,
            'Uncommon': 25,
            'Rare': 15,
            'Epic': 8,
            'Legendary': 2
        }
        
        # Choose rarity based on weights
        rarities = list(rarity_weights.keys())
        weights = list(rarity_weights.values())
        chosen_rarity = random.choices(rarities, weights=weights)[0]
        
        # Get a random weapon of that rarity
        return self.get_random_weapon(chosen_rarity)


# Test the weapon manager
if __name__ == "__main__":
    print("\n" + "="*80)
    print("WEAPON DATABASE TEST")
    print("="*80)
    
    # Load weapons
    wm = WeaponManager('weapons.txt')
    
    # List all weapons
    wm.list_all_weapons()
    
    # Test getting a specific weapon
    print("\n" + "="*80)
    print("TESTING SPECIFIC WEAPON")
    print("="*80)
    excalibur = wm.get_weapon_by_name("Excalibur")
    if excalibur:
        excalibur.display_full_stats()
    
    # Test weapon types
    print("\n" + "="*80)
    print("ALL SWORDS")
    print("="*80)
    swords = wm.get_weapons_by_type("Sword")
    for sword in swords:
        print(f"{sword.get_rarity_color()} {sword.name} - Attack: {sword.attack}")
    
    # Test random weapon
    print("\n" + "="*80)
    print("RANDOM WEAPON DROP")
    print("="*80)
    random_weapon = wm.get_weighted_random_weapon()
    if random_weapon:
        random_weapon.display_full_stats()
    
    # Test weapon usage (durability)
    print("\n" + "="*80)
    print("WEAPON DURABILITY TEST")
    print("="*80)
    test_weapon = wm.get_weapon_by_name("Rusty Sword")
    if test_weapon:
        print(f"Using {test_weapon.name}...")
        for i in range(test_weapon.max_durability + 2):
            broke = test_weapon.use()
            print(f"  Use {i+1}: Durability {test_weapon.durability}/{test_weapon.max_durability}" + 
                  (" - BROKEN!" if broke else ""))
            if broke:
                break