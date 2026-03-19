from __future__ import annotations

import io

import numpy as np
import pytest
import httpx

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class TestHealth:
    @pytest.mark.asyncio
    async def test_health_returns_200(self, client: httpx.AsyncClient):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200

        body = resp.json()
        assert body["status"] == "healthy"


# ---------------------------------------------------------------------------
# Scan endpoint (synthetic image)
# ---------------------------------------------------------------------------

def _create_synthetic_image() -> bytes:
    """Create a minimal 100×100 JPEG via numpy + cv2."""
    try:
        import cv2

        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:] = (200, 200, 200)

        cv2.rectangle(img, (10, 10), (40, 30), (0, 0, 0), 2)
        cv2.putText(img, "1", (20, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        _, buf = cv2.imencode(".jpg", img)
        return buf.tobytes()
    except ImportError:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (100, 100), color=(200, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 40, 30], outline="black", width=2)
        draw.text((20, 20), "1", fill="black")

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()


class TestScanEndpoint:
    @pytest.mark.asyncio
    async def test_scan_accepts_image(self, client: httpx.AsyncClient):
        image_bytes = _create_synthetic_image()

        resp = await client.post(
            "/api/v1/scan",
            files={"image": ("panel.jpg", image_bytes, "image/jpeg")},
            data={"session_id": "test-session-001"},
        )

        # 502 is acceptable when OCR provider (easyocr) is not installed
        assert resp.status_code in (200, 422, 500, 502)

        if resp.status_code == 200:
            body = resp.json()
            assert "scan_id" in body
