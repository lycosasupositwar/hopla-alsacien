import axios from 'axios';

// Define the structure of the analysis parameters
// This should match the backend's AnalysisParameters schema
interface AnalysisParams {
  [key: string]: any;
}

// The base URL for our backend API
const API_BASE_URL = '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Uploads an image and parameters to the backend for analysis.
 * @param imageFile The image file to analyze.
 * @param params The analysis parameters.
 * @param pixelSizeUm The pixel size in micrometers per pixel.
 * @returns The analysis result from the backend.
 */
export const analyzeImage = async (
  imageFile: File,
  params: AnalysisParams,
  pixelSizeUm: number
) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  formData.append('params', JSON.stringify(params));
  formData.append('pixel_size_um', pixelSizeUm.toString());

  try {
    const response = await apiClient.post('/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    // The backend now returns a JSON object that matches the AnalysisResult schema
    // We can define a type for this, but for now, 'any' will suffice.
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      // Throw the error data from the backend response
      throw new Error(error.response.data.error || 'An unknown error occurred during analysis.');
    }
    // Throw a generic error if it's not an Axios error
    throw new Error('An unexpected error occurred.');
  }
};

/**
 * Requests a PDF report for a given analysis result.
 * @param analysisResult The JSON result from a previous analysis.
 * @returns A blob containing the PDF file.
 */
export const getPdfReport = async (analysisResult: any) => {
    try {
        const response = await apiClient.post('/report', analysisResult, {
            responseType: 'blob', // Important: we expect a binary file back
        });
        return response.data;
    } catch (error) {
        if (axios.isAxiosError(error) && error.response) {
            // Since the response is a blob, we need to parse it to get the error message
            const errorJson = await (error.response.data as Blob).text();
            const errorData = JSON.parse(errorJson);
            throw new Error(errorData.error || 'An unknown error occurred while generating the report.');
        }
        throw new Error('An unexpected error occurred.');
    }
}
