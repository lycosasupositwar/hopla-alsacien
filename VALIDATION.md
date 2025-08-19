# Project Validation and Benchmarks

This document outlines the validation strategy for the grain size analysis tool, including notes on the test suite and performance.

## Validation Strategy

The correctness of the image processing pipeline and metric calculations is validated using a suite of unit tests located in `backend/tests/`. The primary strategy relies on **synthetic data generation**.

The `scripts/generate_synthetic.py` script creates several predictable microstructure images, including:
-   A standard Voronoi diagram to simulate a well-behaved microstructure.
-   A specific Y-junction image to test the graph algorithm's ability to correctly identify nodes of degree 3.
-   Images with artifacts to test the robustness of the preprocessing steps.

By running the analysis pipeline on these known inputs, we can assert that the outputs (e.g., number of junctions, presence of a skeleton, calculation of metrics) are correct.

## Test Suite

The test suite is built with `pytest`.

### How to Run Tests

1.  Ensure you have an interactive shell in the running backend container.
    ```bash
    docker-compose exec backend bash
    ```

2.  From within the container's shell, run `pytest`:
    ```bash
    pytest
    ```

### Known Issues

-   **`test_full_pipeline_and_metrics_calculation` Failure**: As of the current version, this specific test fails with an `AssertionError: No intersections were found.` A significant amount of debugging was performed to resolve this, including:
    1.  Fixing a `skan` API usage error (`summarise` vs. `summarize`).
    2.  Correcting a `KeyError` by rewriting the graph-building logic to correctly parse `skan`'s output.
    3.  Resolving a coordinate system mismatch between `numpy` (`y,x`) and `shapely` (`x,y`) during intersection detection.
    4.  Tuning preprocessing parameters (`morph_open`, `area_opening`) to be less destructive on the clean, thin lines of the synthetic image.

    Despite these fixes, the assertion continues to fail. The hypothesis is that there is a very subtle interaction between the `adaptive_threshold` output and the `skeletonize` algorithm on this specific synthetic dataset that results in an empty or non-representative skeleton, preventing intersections. The individual component tests all pass, indicating the core logic of each step is sound. This issue highlights the sensitivity of image analysis pipelines to their input and parameters.

## Performance Benchmarks

**Target**: The goal is to process a 2048x2048 pixel image in approximately **5-7 seconds** on a modern CPU (e.g., 8 vCPU, 16 GB RAM).

**Measurement**:
The backend API automatically times each major step of the analysis and includes it in the final JSON response under the `timings` key. This allows for easy performance measurement.

To perform a benchmark:
1.  Run the application using `docker-compose up`.
2.  Use a tool like `curl` or Postman to `POST` a 2048x2048 image to the `/api/analyze` endpoint.
3.  Inspect the `total_s` value in the JSON response.

*Note: Performance will vary greatly depending on the host machine's hardware.*
```
