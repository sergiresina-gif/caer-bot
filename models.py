from dataclasses import dataclass, field, asdict
from typing import List, Optional, Any, Dict
from datetime import datetime


@dataclass
class Activity:
    xp: int
    gold: int
    label: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Activity":
        return Activity(d.get("xp", 0), d.get("gold", 0), d.get("label", ""), d.get("timestamp", ""))


@dataclass
class Character:
    name: str
    xp: int = 0
    gold: int = 0
    pathfinder_class: Optional[str] = None
    history: List[Activity] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "xp": self.xp,
            "gold": self.gold,
            "pathfinder_class": self.pathfinder_class,
            "history": [a.to_dict() for a in self.history],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Character":
        return Character(
            name=d.get("name", ""),
            xp=d.get("xp", 0),
            gold=d.get("gold", 0),
            pathfinder_class=d.get("pathfinder_class"),
            history=[Activity.from_dict(a) for a in d.get("history", [])],
        )

    def add_xp_gold(self, xp: int, gold: int) -> None:
        self.xp += xp
        self.gold += gold

    def add_activity(self, xp: int, gold: int, label: str, timestamp: str) -> None:
        self.history.append(Activity(xp, gold, label, timestamp))


@dataclass
class User:
    user_name: Optional[str] = None
    user_pfp: Optional[str] = None
    characters: List[Character] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_name": self.user_name,
            "user_pfp": self.user_pfp,
            "characters": [c.to_dict() for c in self.characters]
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "User":
        return User(
            d.get("user_name"),
            d.get("user_pfp"),
            [Character.from_dict(c) for c in d.get("characters", [])]
        )


@dataclass
class Loot:
    title: Optional[str] = None
    description: Optional[str] = None
    xp: Optional[str] = None
    xp_breakdown: Optional[str] = None
    gold: Optional[str] = None
    items: Optional[str] = None
    characters: List[Optional[str]] = field(default_factory=lambda: [None]*10)
    step: int = 0
    last_activity: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Title": self.title,
            "Description": self.description,
            "XP": self.xp,
            "XP Breakdown": self.xp_breakdown,
            "Gold": self.gold,
            "Items": self.items,
            **{f"character_{i+1}": self.characters[i] for i in range(10)},
            "step": self.step,
            "last_activity": self.last_activity,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Loot":
        l = Loot()
        l.title = d.get("Title")
        l.description = d.get("Description")
        l.xp = d.get("XP")
        l.xp_breakdown = d.get("XP Breakdown")
        l.gold = d.get("Gold")
        l.items = d.get("Items")
        for i in range(10):
            l.characters[i] = d.get(f"character_{i+1}")
        l.step = d.get("step", 0)
        l.last_activity = d.get("last_activity")
        return l

    def set_field_by_label(self, label: str, value: str) -> None:
        mapping = {
            "Title": "title",
            "Description": "description",
            "XP": "xp",
            "XP Breakdown": "xp_breakdown",
            "Gold": "gold",
            "Items": "items",
        }
        if label in mapping:
            setattr(self, mapping[label], value)

    def get_field_by_label(self, label: str) -> Optional[str]:
        mapping = {
            "Title": "title",
            "Description": "description",
            "XP": "xp",
            "XP Breakdown": "xp_breakdown",
            "Gold": "gold",
            "Items": "items",
        }
        if label in mapping:
            return getattr(self, mapping[label])
        return None
