from backend.app.services.extract import extract_action_items


def test_extract_action_items_with_prefix_and_non_actionable_sentence():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()

    items = extract_action_items(text)

    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" not in items


def test_extract_action_items_with_assignee_and_due_date():
    text = """
    discuss launch plan
    update deployment checklist owner:alice by 2026-05-02
    weekly status summary
    """.strip()

    items = extract_action_items(text)

    assert "update deployment checklist owner:alice by 2026-05-02" in items
    assert "discuss launch plan" not in items
    assert "weekly status summary" not in items


def test_extract_action_items_filters_question_and_notes():
    text = """
    Can we ship this week?
    notes: this section is context only
    note: reminder for discussion
    """.strip()

    items = extract_action_items(text)

    assert items == []


def test_extract_action_items_deduplicates_whitespace_and_case():
    text = """
    TODO:   update docs
    todo: update docs
    TODO: update   docs
    """.strip()

    items = extract_action_items(text)

    assert items == ["TODO:   update docs"]

