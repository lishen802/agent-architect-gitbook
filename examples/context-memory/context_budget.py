"""Teaching example for chapter 8: allocate a context budget and record a manifest.

Token counts are taken from each item's ``tokens`` field, standing in for a provider's
token counting API. ``estimate_tokens`` is a rough fallback for local experiments
only; it is not any model's tokenizer and can under- or over-count.
"""
from dataclasses import dataclass, field
import math

# Assembly order: stable prefix first, current question last. Instructions and tool
# definitions together form the stable prefix; their relative order is decided by the
# provider's prefix rules (e.g. Anthropic computes cache prefixes as tools -> system ->
# messages), which are independent of the field order written in the request JSON.
ORDER = ('instructions', 'tools', 'state', 'memory', 'evidence', 'history', 'question')
FIXED_KINDS = ('instructions', 'tools')


def estimate_tokens(text):
    """Rough local estimate: one token per CJK character, one per 3 other characters."""
    cjk = sum(1 for c in text if '\u3400' <= c <= '\u9fff' or '\uf900' <= c <= '\ufaff')
    return cjk + math.ceil((len(text) - cjk) / 3)


@dataclass(frozen=True)
class Item:
    id: str
    kind: str
    source: str
    origin: str
    tokens: int
    tenant: str
    required: bool = False
    priority: int = 9          # smaller value is selected earlier among elastic items
    seq: int = 0               # order inside one kind, e.g. time order of history


@dataclass(frozen=True)
class Budget:
    window: int
    reserve_output: int
    margin_ratio: float
    kind_caps: dict = field(default_factory=dict)

    @property
    def available_input(self):
        return self.window - self.reserve_output - math.ceil(self.window * self.margin_ratio)


@dataclass
class Plan:
    status: str                # 'ready' or 'needs_review'
    reason: str
    included: list
    dropped: list              # (item id, reason)
    used: int
    available: int

    def manifest(self):
        return {
            'status': self.status, 'reason': self.reason,
            'available_input': self.available, 'used_input': self.used,
            'included': [dict(id=i.id, kind=i.kind, tokens=i.tokens, source=i.source, origin=i.origin)
                         for i in self.included],
            'dropped': [dict(id=i, reason=r) for i, r in self.dropped],
        }


def _sort_key(item):
    return (ORDER.index(item.kind), item.seq, item.id)


def allocate(items, budget, tenant):
    """Select items for one call.

    Rules: other tenants' items never enter (defence in depth; the real filter belongs in
    the query); fixed and required items must all fit, otherwise the call is not made;
    elastic items are taken whole in priority order, never truncated mid-item.
    """
    for item in items:
        if item.kind not in ORDER:
            raise ValueError(f'unknown kind: {item.kind}')
        if item.tokens <= 0:
            raise ValueError(f'item {item.id} has no token count')
    ids = [i.id for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate item id')

    available = budget.available_input
    dropped = [(i.id, 'tenant_mismatch') for i in items if i.tenant != tenant]
    own = [i for i in items if i.tenant == tenant]
    core = [i for i in own if i.kind in FIXED_KINDS or i.required]
    core_tokens = sum(i.tokens for i in core)
    if core_tokens > available:
        return Plan('needs_review', 'required_over_budget', [], dropped, 0, available)

    used = core_tokens
    per_kind = {}
    chosen = list(core)
    elastic = sorted((i for i in own if i not in core), key=lambda i: (i.priority, _sort_key(i)))
    for item in elastic:
        cap = budget.kind_caps.get(item.kind)
        if cap is not None and per_kind.get(item.kind, 0) + item.tokens > cap:
            dropped.append((item.id, 'kind_cap'))
            continue
        if used + item.tokens > available:
            dropped.append((item.id, 'over_budget'))
            continue
        chosen.append(item)
        used += item.tokens
        per_kind[item.kind] = per_kind.get(item.kind, 0) + item.tokens
    return Plan('ready', 'ok', sorted(chosen, key=_sort_key), dropped, used, available)
