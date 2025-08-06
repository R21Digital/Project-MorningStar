from types import SimpleNamespace

from android_ms11.modes import support_mode


def test_support_mode_prebuff_and_loop_limit(capsys):
    dummy_session = SimpleNamespace(config={"support_leader_name": "Boss"}, profile={"build": {"skills": []}})
    support_mode.run(max_loops=2, session=dummy_session)
    output_lines = capsys.readouterr().out.splitlines()

    prebuff_index = next(
        i for i, line in enumerate(output_lines) if "Pre-buff complete" in line
    )
    follow_indices = [
        i for i, line in enumerate(output_lines) if "Following leader" in line
    ]

    assert len(follow_indices) == 2
    assert prebuff_index < follow_indices[0]
