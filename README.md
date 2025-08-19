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
