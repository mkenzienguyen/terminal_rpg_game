import json
import os

class SaveManager:
    """Manages saving and loading game data"""
    
    def __init__(self, save_file='savegame.json'):
        self.save_file = save_file
    
    def save_game(self, player, world, moves_count):
        """Save the current game state"""
        
        # Prepare player data
        player_data = {
            'name': player.name,
            'health': player.health,
            'max_health': player.max_health,
            'base_attack': player.base_attack,
            'attack': player.attack,
            'defense': player.defense,
            'position': player.position,
            'level': player.level,
            'experience': player.experience,
            'gold': player.gold,
            'moves_count': moves_count
        }
        
        # Save equipped weapon
        if player.equipped_weapon:
            player_data['equipped_weapon'] = {
                'name': player.equipped_weapon.name,
                'attack': player.equipped_weapon.attack,
                'rarity': player.equipped_weapon.rarity,
                'durability': player.equipped_weapon.durability,
                'max_durability': player.equipped_weapon.max_durability,
                'cost': player.equipped_weapon.cost,
                'weapon_type': player.equipped_weapon.weapon_type,
                'special_effect': player.equipped_weapon.special_effect,
                'description': player.equipped_weapon.description
            }
        else:
            player_data['equipped_weapon'] = None
        
        # Save inventory (only weapons for now)
        inventory_data = []
        for item in player.inventory:
            # Check if it's a weapon object
            if hasattr(item, 'name') and hasattr(item, 'attack'):
                inventory_data.append({
                    'name': item.name,
                    'attack': item.attack,
                    'rarity': item.rarity,
                    'durability': item.durability,
                    'max_durability': item.max_durability,
                    'cost': item.cost,
                    'weapon_type': item.weapon_type,
                    'special_effect': item.special_effect,
                    'description': item.description
                })
            else:
                # For non-weapon items (strings, etc.)
                inventory_data.append({'item_name': str(item)})
        
        player_data['inventory'] = inventory_data
        
        # Save world data
        world_data = {
            'width': world.width,
            'height': world.height,
            'discovered': list(world.discovered)  # Convert set to list for JSON
        }
        
        # Combine all data
        save_data = {
            'player': player_data,
            'world': world_data,
            'version': '1.0'
        }
        
        # Write to file
        try:
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"\n💾 Game saved successfully to {self.save_file}!")
            return True
        except Exception as e:
            print(f"\n❌ Error saving game: {e}")
            return False
    
    def load_game(self, player, world, weapon_manager):
        """Load a saved game state"""
        
        if not os.path.exists(self.save_file):
            print(f"\n❌ No save file found: {self.save_file}")
            return None
        
        try:
            with open(self.save_file, 'r') as f:
                save_data = json.load(f)
            
            # Load player data
            player_data = save_data['player']
            player.name = player_data['name']
            player.health = player_data['health']
            player.max_health = player_data['max_health']
            player.base_attack = player_data['base_attack']
            player.attack = player_data['attack']
            player.defense = player_data['defense']
            player.position = player_data['position']
            player.level = player_data['level']
            player.experience = player_data['experience']
            player.gold = player_data['gold']
            
            # Load equipped weapon
            if player_data['equipped_weapon']:
                weapon_data = player_data['equipped_weapon']
                # Try to get weapon from weapon manager
                equipped = weapon_manager.get_weapon_by_name(weapon_data['name'])
                if equipped:
                    # Restore durability
                    equipped.durability = weapon_data['durability']
                    player.equipped_weapon = equipped
                else:
                    print(f"⚠️  Warning: Could not find weapon {weapon_data['name']}")
            else:
                player.equipped_weapon = None
            
            # Load inventory
            player.inventory = []
            for item_data in player_data['inventory']:
                if 'name' in item_data:  # It's a weapon
                    weapon = weapon_manager.get_weapon_by_name(item_data['name'])
                    if weapon:
                        # Restore durability
                        weapon.durability = item_data['durability']
                        player.inventory.append(weapon)
                elif 'item_name' in item_data:  # It's a regular item
                    player.inventory.append(item_data['item_name'])
            
            # Load world data
            world_data = save_data['world']
            world.discovered = set(tuple(pos) for pos in world_data['discovered'])
            
            # Return moves count
            moves_count = player_data.get('moves_count', 0)
            
            print(f"\n📂 Game loaded successfully!")
            print(f"   Welcome back, {player.name}!")
            print(f"   Level {player.level} | HP: {player.health}/{player.max_health}")
            return moves_count
            
        except Exception as e:
            print(f"\n❌ Error loading game: {e}")
            return None
    
    def save_exists(self):
        """Check if a save file exists"""
        return os.path.exists(self.save_file)
    
    def delete_save(self):
        """Delete the save file"""
        try:
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
                print(f"\n🗑️  Save file deleted: {self.save_file}")
                return True
            else:
                print(f"\n⚠️  No save file to delete")
                return False
        except Exception as e:
            print(f"\n❌ Error deleting save: {e}")
            return False


def display_save_info(save_file='savegame.json'):
    """Display information about a save file without loading it"""
    
    if not os.path.exists(save_file):
        print(f"\n❌ No save file found: {save_file}")
        return
    
    try:
        with open(save_file, 'r') as f:
            save_data = json.load(f)
        
        player_data = save_data['player']
        
        print("\n" + "="*50)
        print("  SAVE FILE INFO")
        print("="*50)
        print(f"  Character: {player_data['name']}")
        print(f"  Level: {player_data['level']}")
        print(f"  Health: {player_data['health']}/{player_data['max_health']}")
        print(f"  Attack: {player_data['attack']}")
        print(f"  Defense: {player_data['defense']}")
        print(f"  Gold: {player_data['gold']}")
        print(f"  Experience: {player_data['experience']}")
        print(f"  Position: {tuple(player_data['position'])}")
        
        if player_data['equipped_weapon']:
            weapon = player_data['equipped_weapon']
            print(f"  Equipped: {weapon['name']}")
        
        print(f"  Inventory Items: {len(player_data['inventory'])}")
        print(f"  Moves: {player_data.get('moves_count', 'Unknown')}")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error reading save file: {e}")


# Test the save system
if __name__ == "__main__":
    print("Save/Load System Module")
    print("=" * 50)
    
    sm = SaveManager()
    
    if sm.save_exists():
        print(f"\n✓ Save file exists: {sm.save_file}")
        display_save_info()
    else:
        print(f"\n✗ No save file found: {sm.save_file}")