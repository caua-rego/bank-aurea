import os
from flask import Blueprint, send_from_directory, current_app, Response

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/openapi.yaml")
def openapi_spec():
    docs_dir = os.path.abspath(os.path.join(current_app.root_path, '..', 'docs'))
    return send_from_directory(
        directory=docs_dir,
        path='openapi.yaml',
        mimetype='application/yaml'
    )


@docs_bp.route("/docs")
def redoc():
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Bank Aurea API Docs</title>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Inter:400,600" />
        <style>
          body { margin: 0; padding: 0; font-family: Inter, sans-serif; }
          header { padding: 12px 20px; background: #0f172a; color: #e2e8f0; }
          header h1 { margin: 0; font-size: 18px; letter-spacing: 0.5px; }
          .redoc-container { height: calc(100vh - 52px); }
        </style>
      </head>
      <body>
        <header><h1>Bank Aurea API</h1></header>
        <redoc spec-url="/openapi.yaml"></redoc>
        <script src="https://cdn.redoc.ly/redoc/v2.4.0/bundles/redoc.standalone.js"></script>
      </body>
    </html>
    """
    return Response(html, mimetype="text/html")
