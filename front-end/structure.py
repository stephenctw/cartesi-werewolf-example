from dataclasses import dataclass
from enum import Enum
from typing import List

class Role(Enum):
    WEREWOLF = 1
    VILLAGER = 2
    MODERATOR = 3

@dataclass
class Player:
  id: str
  role: Role
  is_alive: bool
  public_key: str
  # private_key: str

@dataclass
class GameState:
  is_finished: bool
  is_day: bool
  round: int
  players: List[Player] # assume the first player is moderator
