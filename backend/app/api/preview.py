import json
from flask import Blueprint, request, jsonify

from ..utils.image_utils import read_image_from_bytes, encode_image_to_base64
from ..processing.preprocess import preprocess_image
from ..schemas.models import AnalysisParameters

preview_bp = Blueprint('preview', __name__)

@preview_bp.route('/preprocess', methods=['POST'])
def preprocess_preview():
    """
    Provides a preview of the image preprocessing step.
    Accepts an image and preprocessing parameters, and returns the
    resulting binary image without running the full analysis.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()

    try:
        original_image = read_image_from_bytes(image_bytes)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Load and merge parameters
    try:
        default_params = AnalysisParameters()
        user_params_dict = json.loads(request.form.get('params', '{}'))

        # Create a new model instance with updated parameters
        # This works for both Pydantic v1 and v2
        updated_params_dict = default_params.dict()
        updated_params_dict.update(user_params_dict)
        params = AnalysisParameters(**updated_params_dict)

    except (json.JSONDecodeError, TypeError) as e:
        return jsonify({"error": f"Invalid parameters: {str(e)}"}), 400

    try:
        # Perform only the preprocessing step
        binary_image = preprocess_image(
            original_image,
            params.gaussian_sigma,
            params.adaptive_block_size,
            params.adaptive_offset,
            params.morph_open_kernel,
            params.area_opening_min_size_px
        )

        # Encode the result as base64
        base64_image = encode_image_to_base64(binary_image)

        return jsonify({
            "preview_image_base64": base64_image
        })

    except Exception as e:
        return jsonify({
            "error": f"An error occurred during preprocessing: {str(e)}"
        }), 500
