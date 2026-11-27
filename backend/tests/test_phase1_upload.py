"""Runtime upload boundary tests for unsafe content and filenames."""

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    ("name", "body", "content_type", "status"),
    [
        ("../../other.csv", b"txid,fee\na,1\n", "text/csv", 400),
        ("..\\..\\other.csv", b"txid,fee\na,1\n", "text/csv", 400),
        ("bad.csv", b'{"txid":"a"}', "application/json", 400),
        ("archive.csv", b"PK\x03\x04" + b"x" * 100, "text/csv", 400),
        ("nested.csv", b"txid,fee\na,1\nPK\x03\x04", "text/csv", 400),
        ("empty.csv", b"", "text/csv", 400),
        ("binary.csv", b"txid,fee\n\x00\xff", "text/csv", 400),
        (
            "bad.xml",
            b'<!DOCTYPE x [<!ENTITY a SYSTEM "file:///etc/passwd">]><transactions>&a;</transactions>',
            "application/xml",
            400,
        ),
    ],
)
def test_upload_rejects_unsafe_inputs(name, body, content_type, status):
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/datasets/upload", files={"file": (name, body, content_type)}
        )
    assert response.status_code == status
    assert all(
        item not in response.text
        for item in ("Traceback", "SELECT", "D:\\", "/etc/passwd", "PK\\x03")
    )


def test_upload_size_cap(monkeypatch):
    monkeypatch.setenv("NIRIKSHAK_UPLOAD_MAX_MB", "1")
    body = b"txid,fee\n" + b"a" * (1024 * 1024)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/datasets/upload", files={"file": ("large.csv", body, "text/csv")}
        )
    assert response.status_code == 413
    assert response.json()["detail"] == "Upload size limit exceeded"
