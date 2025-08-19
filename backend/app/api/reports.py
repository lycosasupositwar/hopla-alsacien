from flask import Blueprint, request, jsonify, render_template, Response
from weasyprint import HTML
import json

from ..schemas.models import AnalysisResult

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/report', methods=['POST'])
def generate_report():
    """
    Generates a PDF report from an analysis result JSON.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    try:
        # Validate the incoming data against our Pydantic model
        analysis_result = AnalysisResult.model_validate(data)
    except Exception as e:
        return jsonify({"error": "Invalid analysis result data provided", "details": str(e)}), 400

    # Render the HTML template with the analysis data
    # The template will use the base64 strings directly in <img> tags
    html_out = render_template("report_template.html", result=analysis_result.model_dump())

    # Generate PDF in memory
    pdf_bytes = HTML(string=html_out).write_pdf()

    # Return the PDF as a downloadable file
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename=report_{analysis_result.image_id[:8]}.pdf"}
    )
