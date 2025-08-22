# Automated Grain Size Analysis Tool

This project provides a full-stack web application for performing automated intercept analysis on microstructure images to determine grain size, conforming to standards like ASTM E112. It features a React frontend and a Python (Flask) backend with a sophisticated image processing pipeline.

## Features

-   **Image Upload**: Supports standard image formats (PNG, JPG, TIFF).
-   **Calibration**: Allows user to specify pixel size (µm/px) or magnification.
-   **Robust Preprocessing**: Uses Gaussian blur and adaptive thresholding to handle noise and uneven illumination.
-   **Topological Analysis**: Extracts a skeleton from grain boundaries and converts it into a graph structure for analysis.
-   **Automated Intercepts**: Generates linear or circular test patterns and calculates intersections with the grain boundary skeleton.
-   **Standardized Metrics**: Calculates mean intercept length (ℓ), ASTM grain size number (G), and grain density (N_AE).
-   **Interactive Visualization**: A canvas-based UI allows users to view the original image with overlays for the skeleton, test patterns, and intersections.
-   **Data Export**: Results can be exported as a comprehensive PDF report.
-   **Batch Processing**: The API is designed to support batch processing (though the UI for it is a future extension).
-   **Containerized**: The entire application is containerized with Docker for easy deployment and reproducibility.

## Getting Started

### Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)
-   A `bash` compatible shell.

### Quickstart with Demo

The included `demo.sh` script automates the entire process of building the application, generating test data, and running a sample analysis.

1.  **Make the script executable:**
    ```bash
    chmod +x demo.sh
    ```

2.  **Run the demo:**
    ```bash
    ./demo.sh
    ```

This script will:
-   Build and start the frontend and backend Docker containers.
-   Generate synthetic microstructure images in `examples/input/`.
-   Run an analysis on a sample image.
-   Save the JSON result to `examples/output/analysis_result.json`.
-   Generate a PDF report from the result and save it to `examples/output/demo_report.pdf`.

Once the script is complete, you can:
-   **Access the web UI** at `http://localhost:5173`.
-   **View the generated report** in the `examples/output/` directory.

## Future Improvements

### AI-Powered Twin Detection

The current implementation uses a classical computer vision approach (Hough Transform) to detect and remove twinning lines in austenitic stainless steel microstructures. While effective for well-defined, straight twins, this method can be limited by image noise and variations in twin morphology.

A more robust and powerful approach would be to use a deep learning model for **semantic segmentation**, such as a **U-Net architecture**.

**How it would work:**

1.  **Data Annotation**: A dataset of microstructure images would be manually annotated, with each pixel labeled as "grain boundary," "twin," or "background."
2.  **Model Training**: The U-Net model would be trained on this annotated dataset. The model learns the complex visual features and spatial relationships that differentiate twins from actual grain boundaries.
3.  **Inference**: Once trained, the model can take a new image and produce a pixel-wise segmentation map, accurately classifying each component. This would allow for the direct exclusion of twins from the grain size calculation with high precision.

**Advantages**:
-   **Higher Accuracy**: Superior ability to distinguish between complex and ambiguous features compared to classical algorithms.
-   **Robustness**: Less sensitive to variations in illumination, staining, and image quality.
-   **Flexibility**: Can be trained to recognize other microstructural features simultaneously.

This AI-based approach represents a significant potential enhancement for the tool, paving the way for more accurate and reliable automated analysis across a wider range of materials and conditions.

### Manual Installation

1.  **Build and start the containers:**
    ```bash
    docker-compose up -d --build
    ```

2.  **Access the application:**
    -   Frontend: `http://localhost:5173`
    -   Backend API: `http://localhost:8000`

3.  **To stop the application:**
    ```bash
    docker-compose down
    ```

## Project Structure

```
.
├── backend/            # Python Flask Backend
│   ├── app/            # Main application source
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/           # React Frontend
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── examples/           # Example input images and output results
├── scripts/            # Helper scripts (e.g., synthetic data generation)
├── docker-compose.yml  # Orchestrates the services
├── demo.sh             # Automated demo script
└── README.md           # This file
```

## API Endpoints

-   `POST /api/analyze`: The main analysis endpoint.
    -   **Body**: `multipart/form-data`
    -   `image`: The image file.
    -   `pixel_size_um`: (float) The calibration value.
    -   `params`: (JSON string) A JSON object of the analysis parameters.
    -   **Returns**: A detailed JSON object (`AnalysisResult`) with metrics, overlays, and other data.

-   `POST /api/report`: Generates a PDF report.
    -   **Body**: `application/json`
    -   The JSON object received from a successful `/api/analyze` call.
    -   **Returns**: A `application/pdf` file.
```
