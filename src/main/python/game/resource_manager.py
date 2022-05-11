import pygame as pg
import json
import os

import ctypes.wintypes

class ResourceManager:

    def __init__(self, username, file_name):
        self.username = username
        
        CSIDL_PERSONAL = 5       # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value

        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        
        self.file_path = buf.value + "\\SmartLMS Gamification Experiment"
        
        if not os.path.exists(self.file_path):
            os.mkdir(self.file_path)

        self.file_path += "\\" + file_name + ".hse"

        try:
            with open(self.file_path) as f:
                data = json.load(f)
                if "resources" in data:
                    self.resources = data["resources"]
                else:
                    self.resources = {
                        "roadblocks": 5,
                        "money": 150,
                        "jobs": 0,
                        "happiness": 0,
                        "globalization": 0,
                        "population": 0
                    }
                    self.save_resources()
                f.close()
        except IOError:
            self.resources = {
                "roadblocks": 5,
                "money": 150,
                "jobs": 0,
                "happiness": 0,
                "globalization": 0,
                "population": 0
            }
            self.save_resources()

        self.costs = {
            "tree": {"money": 10},
            "road": {"roadblocks": 1},
            "low": {"money": 100, "globalization": 0},
            "medium": {"money": 500, "globalization": 10},
            "high": {"money": 2000, "globalization": 50},
            "skyscraper": {"money": 10000, "globalization": 70},
            "park": {"money": 3500, "globalization": 0},
            "of": {"money": 100000, "globalization": 100}
        }

        self.immediate_profits = {
            "low": {"population": 3},
            "medium": {"population": 30},
            "high": {"jobs": 50},
            "skyscraper": {"jobs": 500},
            "park": {"happiness": 20},
            "of": {"happiness": 1000}
        }
        
        self.resource_names = {
            "roadblocks": "Roads",
            "money": "Money",
            "jobs": "Jobs",
            "happiness": "Happiness",
            "globalization": "Globalization",
            "population": "Population"
        }

    def apply_difference(self, difference, is_fundamental):
        received_rewards = {}
        rewards_table = {
            "A": {"happiness": 50, "globalization": 3, "roadblocks": 2},
            "B": {"happiness": 20, "roadblocks": 1}
        }
        for dif, val in difference.items():
            print(val)
            if dif in rewards_table:
                for reward, reward_val in rewards_table[dif].items():
                    if reward != "roadblocks":
                        self.resources[reward] += (val * reward_val)
                        if reward in received_rewards:
                            received_rewards[reward] += (val * reward_val)
                        else:
                            if val * reward_val != 0:
                                received_rewards[reward] = (val * reward_val)
                    else:
                        if is_fundamental == True:
                            self.resources[reward] += (val * reward_val)
                            if reward in received_rewards:
                                received_rewards[reward] += (val * reward_val)
                            else:
                                if val * reward_val != 0:
                                    received_rewards[reward] = (val * reward_val)
        self.save_resources()
        return received_rewards

    def apply_cost_to_resource(self, building):
        for resource, cost in self.costs[building].items():
            if resource != "globalization":
                self.resources[resource] -= cost
        self.save_resources()

    def apply_immediate_profits(self, building):
        for resource, cost in self.immediate_profits[building].items():
            self.resources[resource] += cost
        self.save_resources()

    def can_build(self, building):
        affordable = True
        for resource, cost in self.costs[building].items():
            if cost > self.resources[resource]:
                affordable = False
        return affordable

    def save_resources(self):
        total_data = {}
        try:
            with open(self.file_path) as f:
                total_data = json.load(f)
                total_data["resources"] = self.resources
                f.close()
        except IOError:
            total_data["resources"] = self.resources

        with open(self.file_path, 'w+') as f:
            f.seek(0)
            json.dump(total_data, f, indent=4)
            f.truncate()
        f.close()
