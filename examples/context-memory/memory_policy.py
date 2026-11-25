"""Teaching example for chapter 8: system checks before a memory write, and filters on read.

The rules are a design illustration, not a complete security control. Detecting
instruction-like text is only a review signal; authorization still happens at the tool
execution boundary.
"""
import re

KINDS = ('preference', 'service_fact', 'experience')
ORIGINS = ('user_statement', 'authoritative_system', 'human_confirmed', 'model_inference')
MAX_CHARS = 300
INSTRUCTION_LIKE = re.compile(r'忽略|无视|以后.{0,30}(直接|总是|一律)|ignore (all|previous)|always ', re.I)


def check_write(candidate, ctx, known_refs):
    """Return (decision, reasons); decision is 'accept', 'pending_review' or 'reject'.

    ctx comes from the authenticated request (tenant, user), never from model output.
    known_refs are evidence or record ids that exist in this task.
    """
    reasons = []
    required = ('key', 'kind', 'content', 'origin', 'scope', 'source_refs')
    if any(f not in candidate for f in required):
        return 'reject', ['missing_field']
    kind, origin, scope = candidate['kind'], candidate['origin'], candidate['scope']
    if kind not in KINDS or origin not in ORIGINS:
        return 'reject', ['unknown_kind_or_origin']
    if scope.get('tenant') != ctx['tenant']:
        reasons.append('tenant_mismatch')
    if kind == 'preference' and scope.get('user') != ctx['user']:
        reasons.append('user_scope_mismatch')
    if not candidate['source_refs'] or any(r not in known_refs for r in candidate['source_refs']):
        reasons.append('unknown_source_ref')
    content = candidate['content']
    if not content.strip() or len(content) > MAX_CHARS:
        reasons.append('content_size')
    if kind == 'service_fact' and not candidate.get('valid_until'):
        reasons.append('missing_valid_until')
    if reasons:
        return 'reject', reasons

    review = []
    if origin == 'model_inference':
        review.append('model_inference')          # model output never becomes trusted memory directly
    if kind == 'experience' and origin != 'human_confirmed':
        review.append('experience_needs_confirmation')
    if kind == 'preference' and origin != 'user_statement':
        review.append('preference_not_stated_by_user')
    if INSTRUCTION_LIKE.search(content):
        review.append('instruction_like')
    return ('pending_review', review) if review else ('accept', [])


def apply_write(store, candidate, decision, now):
    """Append a new version; older versions stay for audit and are marked superseded."""
    status = 'trusted' if decision == 'accept' else 'pending'
    versions = [e for e in store if e['scope'] == candidate['scope'] and e['key'] == candidate['key']]
    version = max((e['version'] for e in versions), default=0) + 1
    if status == 'trusted':
        for e in versions:
            if e['status'] == 'trusted':
                e['status'] = 'superseded'
    entry = dict(candidate, version=version, status=status, created_at=now)
    store.append(entry)
    return entry


def select_for_context(store, ctx, now):
    """Entries a call may read: same tenant, own user scope, trusted, not expired."""
    out = []
    for e in store:
        scope = e['scope']
        if scope.get('tenant') != ctx['tenant']:
            continue
        if scope.get('user') not in (None, ctx['user']):
            continue
        if e['status'] != 'trusted':
            continue
        if e.get('valid_until') and e['valid_until'] <= now:
            continue
        out.append(e)
    return sorted(out, key=lambda e: (e['key'], e['version']))


def delete_subject(store, tenant, user):
    """Remove a user's entries; the caller must also clear summaries, indexes and caches."""
    before = len(store)
    store[:] = [e for e in store if not (e['scope'].get('tenant') == tenant and e['scope'].get('user') == user)]
    return before - len(store)
