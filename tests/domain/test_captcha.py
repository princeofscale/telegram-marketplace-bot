from bot.modules.captcha.challenge import CAPTCHA_PASS_CALLBACK, CaptchaChallenge, verify_captcha_callback


def test_inline_button_captcha_accepts_expected_callback() -> None:
    challenge = CaptchaChallenge.inline_button()

    assert challenge.text_key == "captcha prompt"
    assert challenge.pass_callback_data == CAPTCHA_PASS_CALLBACK
    assert challenge.style == "success"
    assert verify_captcha_callback(CAPTCHA_PASS_CALLBACK)


def test_inline_button_captcha_rejects_unrelated_callback() -> None:
    assert not verify_captcha_callback("menu")
    assert not verify_captcha_callback(None)
