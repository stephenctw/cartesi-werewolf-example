from dataclasses import dataclass
from enum import Enum
from typing import List

class Role(Enum):
    WEREWOLF = 1
    VILLAGER = 2
    MODERATOR = 3

@dataclass
class Player:
  role: Role
  is_alive: bool
  pubKey: str
  private_key: str

@dataclass
class GameState:
  is_finished: bool
  is_day: bool
  round: int
  players: List[Player]
