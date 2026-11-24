from app.models import Action, Plan, Task
import pytest

from app.planner import _align_calendar_dates, _validate_plan_coverage, create_plan


def test_calendar_template_uses_date_from_user_text() -> None:
    plan = create_plan("Schedule my internship joining day in Hyderabad on January 5 in Google Calendar")
    action = plan.tasks[0].actions[0]
    assert action.tool == "calendar_create_event"
    assert action.args["date"] == "January 5"


def test_calendar_llm_shape_is_normalized_to_cue_date() -> None:
    plan = Plan(
        event_id="evt_test",
        summary="Schedule event",
        tasks=[Task(
            id="t1",
            title="Next steps",
            actions=[Action(
                id="a1",
                app="calendar",
                tool="calendar_create_event",
                args={"summary": "Joining day", "start": {"date": "2024-01-05T00:00:00Z"}},
            )],
        )],
    )
    normalized = _align_calendar_dates(plan, "Schedule it on January 5")
    args = normalized.tasks[0].actions[0].args
    assert args["date"] == "January 5"
    assert "start" not in args


def test_internship_plan_cannot_omit_core_actions() -> None:
    plan = Plan(
        event_id="evt_test",
        summary="Internship",
        tasks=[Task(
            id="t1",
            title="Next steps",
            actions=[Action(
                id="a1",
                app="notion",
                tool="notion_create_page",
                args={"title": "Checklist"},
            )],
        )],
    )
    with pytest.raises(ValueError, match="omitted required actions"):
        _validate_plan_coverage(plan, "I got an internship in Hyderabad starting January 5")

