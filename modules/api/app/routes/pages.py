"""Page routes (SP-09). The index page is static HTML; the news grid is loaded by the browser from
GET /api/news (FE-BE wiring, contract getNews). No business logic runs in this route.
"""

from __future__ import annotations

from flask import Blueprint, render_template

pages_bp: Blueprint = Blueprint("pages", __name__)


@pages_bp.get("/")
def index() -> str:
    """News grid page: modules/ui/templates/index.html."""
    return render_template("index.html")
