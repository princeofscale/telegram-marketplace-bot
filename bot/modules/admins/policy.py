from __future__ import annotations


def parse_admin_user_ids(value: str | None) -> frozenset[int]:
    if not value:
        return frozenset()

    user_ids: set[int] = set()
    for raw_item in value.replace(";", ",").split(","):
        item = raw_item.strip()
        if not item:
            continue
        user_ids.add(int(item))

    return frozenset(user_ids)


def is_default_admin_user(user_id: int, admin_user_ids: frozenset[int]) -> bool:
    return user_id in admin_user_ids
