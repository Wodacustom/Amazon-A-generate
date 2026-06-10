from app.services.auth_accounts import generate_redemption_code, hash_password, normalize_email, verify_password


def test_password_hash_roundtrip():
    password_hash = hash_password("secret-pass")

    assert password_hash != "secret-pass"
    assert verify_password("secret-pass", password_hash)
    assert not verify_password("wrong-pass", password_hash)


def test_normalize_email():
    assert normalize_email("  User@Example.COM ") == "user@example.com"


def test_generate_redemption_code_has_fixed_prefix():
    code = generate_redemption_code()

    assert code.startswith("AP")
    assert len(code) == 20
