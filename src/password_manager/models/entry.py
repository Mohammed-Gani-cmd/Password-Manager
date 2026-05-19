from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Entry:
    title: str
    username: str
    password: str
    notes: str = ""
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self):
        return asdict(self)
