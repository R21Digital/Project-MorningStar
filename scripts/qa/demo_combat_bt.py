from __future__ import annotations

from behavior_tree import Sequence, Selector, Condition, Action, Status


def has_target(ctx):
    return bool(ctx.get('has_target'))


def in_range(ctx):
    return ctx.get('distance', 999) <= ctx.get('max_range', 35)


def use_ability(name):
    def _fn(ctx):
        ctx.setdefault('log', []).append(f'cast:{name}')
        return Status.SUCCESS
    return _fn


tree = Sequence([
    Condition(has_target),
    Selector([
        Sequence([Condition(in_range), Action(use_ability('primary'))]),
        Action(use_ability('gap_close')),
    ]),
])


def tick(ctx: dict) -> str:
    return tree.tick(ctx)


