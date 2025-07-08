from core.dashboard_utils import group_quests_by_category


def test_group_quests_by_category_empty():
    assert group_quests_by_category() == {}
