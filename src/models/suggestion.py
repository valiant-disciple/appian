from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class CodeChange:
    old: Optional[str]
    new: str
    status: str

@dataclass
class Preview:
    html: str

@dataclass
class Suggestion:
    changes: Dict[str, CodeChange]
    preview: Preview

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Suggestion':
        changes = {
            k: CodeChange(
                old=v.get('old'),
                new=v['new'],
                status=v['status']
            )
            for k, v in data['changes'].items()
        }
        preview = Preview(html=data['preview']['html'])
        return cls(changes=changes, preview=preview) 