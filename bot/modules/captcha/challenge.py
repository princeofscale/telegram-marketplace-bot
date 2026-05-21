from __future__ import annotations
from dataclasses import dataclass

CAPTCHA_PASS_CALLBACK = "captcha:pass"  # noqa: S105
DEFAULT_STYLE = "success"


@dataclass(frozen=True)
class CaptchaChallenge:
    text_key: str
    pass_callback_data: str
    style: str = DEFAULT_STYLE

    @classmethod
    def inline_button(cls) -> CaptchaChallenge:
        return cls(text_key="captcha prompt", pass_callback_data=CAPTCHA_PASS_CALLBACK, style=DEFAULT_STYLE)


def verify_captcha_callback(callback_data: str | None) -> bool:
    return callback_data == CAPTCHA_PASS_CALLBACK
