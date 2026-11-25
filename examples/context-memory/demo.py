"""Print the context manifest for the chapter 8 scenario."""
import json
from pathlib import Path
from context_budget import Budget, Item, allocate

ROOT = Path(__file__).resolve().parent


def load(path=ROOT / 'scenario.json'):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    budget = Budget(**data['budget'])
    items = [Item(**i) for i in data['items']]
    return data['tenant'], budget, items


if __name__ == '__main__':
    tenant, budget, items = load()
    print(json.dumps(allocate(items, budget, tenant).manifest(), ensure_ascii=False, indent=2))
