from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InMemoryStore:
    tasks: dict[str, dict] = field(default_factory=dict)
    results: dict[str, dict] = field(default_factory=dict)
    result_versions: dict[str, list[dict]] = field(default_factory=dict)
    sessions: dict[str, dict] = field(default_factory=dict)
    style_memories: dict[str, dict] = field(default_factory=dict)
    tryon_jobs: dict[str, dict] = field(default_factory=dict)
    tryon_items: dict[str, list[dict]] = field(default_factory=dict)
    products: dict[str, dict] = field(default_factory=dict)
    files: dict[str, dict] = field(default_factory=dict)
    mockup_templates: dict[str, dict] = field(default_factory=dict)


store = InMemoryStore()
