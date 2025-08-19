#!/bin/bash

# A script to demonstrate the full application lifecycle.

echo "--- Starting Grain Size Analysis Demo ---"

# 1. Build and start the Docker containers
echo "Step 1: Building and starting services with Docker Compose..."
docker-compose up -d --build
if [ $? -ne 0 ]; then
    echo "Error: Docker Compose failed to build or start. Aborting."
    exit 1
fi

echo "Waiting for services to become healthy (approx. 30 seconds)..."
sleep 30

# 2. Generate synthetic test data
echo "Step 2: Generating synthetic images inside the backend container..."
docker-compose exec backend python3 scripts/generate_synthetic.py
if [ $? -ne 0 ]; then
    echo "Error: Failed to generate synthetic data. Aborting."
    docker-compose down
    exit 1
fi
echo "Synthetic data generated in examples/input/"

# 3. Run analysis on a synthetic image
echo "Step 3: Running analysis on 'synthetic_voronoi_standard.png'..."
# Note: The result is piped to jq for pretty-printing if installed.
ANALYSIS_RESULT=$(curl -s -X POST \
  -F "image=@./examples/input/synthetic_voronoi_standard.png" \
  -F "pixel_size_um=1.0" \
  -F "params={}" \
  http://localhost:8050/api/analyze)

if [ -z "$ANALYSIS_RESULT" ] || [[ "$ANALYSIS_RESULT" == *"error"* ]]; then
    echo "Error: Analysis API call failed."
    echo "Response: $ANALYSIS_RESULT"
    docker-compose down
    exit 1
fi

# Save the result to a file
echo "$ANALYSIS_RESULT" > examples/output/analysis_result.json
echo "Analysis complete. JSON result saved to examples/output/analysis_result.json"

# 4. Generate a PDF report from the analysis
echo "Step 4: Generating PDF report from the analysis result..."
curl -s -X POST \
  -H "Content-Type: application/json" \
  --data "@./examples/output/analysis_result.json" \
  http://localhost:8050/api/report \
  --output examples/output/demo_report.pdf

if [ $? -ne 0 ] || [ ! -s "examples/output/demo_report.pdf" ]; then
    echo "Error: PDF report generation failed."
    docker-compose down
    exit 1
fi
echo "PDF report saved to examples/output/demo_report.pdf"


echo -e "\n--- Demo Complete! ---"
echo "You can now:"
echo "1. Access the frontend UI at http://localhost:8080"
echo "2. View the generated report at examples/output/demo_report.pdf"
echo "3. View the raw JSON result at examples/output/analysis_result.json"
echo -e "\nTo stop the application, run:"
echo "docker-compose down"
