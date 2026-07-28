from arch_bot.text import split_message


def test_short_message_is_unchanged() -> None:
    assert split_message("hello", limit=10) == ["hello"]


def test_long_message_prefers_newline() -> None:
    assert split_message("first\nsecond", limit=7) == ["first", "second"]


def test_long_word_is_hard_split() -> None:
    assert split_message("abcdefgh", limit=3) == ["abc", "def", "gh"]


def test_invalid_limit_is_rejected() -> None:
    try:
        split_message("hello", limit=0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
