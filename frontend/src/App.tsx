import React, { useState } from 'react';
import { ThemeProvider } from "@/components/theme-provider"
import { QueryClient, QueryClientProvider, useMutation } from "@tanstack/react-query"
import { analyzeImage, getPdfReport } from './lib/api';

// UI Components
import { Button } from '@/components/ui/button';
import { ModeToggle } from '@/components/theme-toggle';

// App Components
import ImageUploader from "@/components/ImageUploader"
import CalibrationPanel from "@/components/CalibrationPanel"
import PreprocessPanel from "@/components/PreprocessPanel"
import SkeletonCanvas from "@/components/SkeletonCanvas"
import ResultsTable from "@/components/ResultsTable"
import HistogramCard from "@/components/HistogramCard"

const queryClient = new QueryClient();

// Define a more specific type for the result to improve type safety
type AnalysisResult = {
  image_id: string;
  metrics: any;
  intersections: any[];
  edges_stats: { edges: any[] };
  motifs: any[];
  // other fields...
} | null;


function MainApp() {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [pixelSize, setPixelSize] = useState<number>(1.0);
  const [params, setParams] = useState({
    gaussian_sigma: 1.0,
    adaptive_block_size: 101,
    adaptive_offset: 10,
  });
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const analysisMutation = useMutation({
    mutationFn: () => {
      if (!imageFile) throw new Error("Please select an image file.");
      // Clear previous results and errors when starting a new analysis
      setAnalysisResult(null);
      setAnalysisError(null);
      return analyzeImage(imageFile, params, pixelSize);
    },
    onSuccess: (data) => {
      setAnalysisResult(data);
      setAnalysisError(null); // Clear any previous errors on success
    },
    onError: (error: Error) => {
      setAnalysisError(error.message);
      setAnalysisResult(null); // Clear results on error
    },
  });

  const reportMutation = useMutation({
    mutationFn: () => {
      if (!analysisResult) throw new Error("No analysis result to report.");
      return getPdfReport(analysisResult);
    },
    onSuccess: (data) => {
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report-${analysisResult?.image_id.substring(0, 8)}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
    onError: (error: Error) => {
      alert(`Report generation failed: ${error.message}`);
    }
  });

  return (
    <ThemeProvider defaultTheme="dark" storageKey="grain-size-analysis-theme">
      <div className="min-h-screen bg-background text-foreground">
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container flex h-14 items-center">
            <h1 className="text-xl font-bold">Automated Grain Size Analysis</h1>
            <div className="flex flex-1 items-center justify-end">
              <ModeToggle />
            </div>
          </div>
        </header>

        <main className="container mx-auto p-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 space-y-6">
              <div className="p-4 border rounded-lg space-y-4">
                <ImageUploader onFileSelect={setImageFile} />
                <CalibrationPanel onPixelSizeChange={setPixelSize} />
              </div>
              <div className="p-4 border rounded-lg">
                <PreprocessPanel params={params} onParamsChange={setParams} />
              </div>
               <div className="p-4 border rounded-lg">
                <h2 className="text-lg font-semibold mb-2">3. Analysis</h2>
                <Button
                  className="w-full"
                  onClick={() => analysisMutation.mutate()}
                  disabled={!imageFile || analysisMutation.isPending}
                >
                  {analysisMutation.isPending ? 'Analyzing...' : 'Analyze'}
                </Button>
                {analysisError && (
                  <div className="mt-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                    <p className="text-sm font-bold text-destructive">Analysis Failed</p>
                    <p className="text-sm text-destructive/90">{analysisError}</p>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:col-span-2 space-y-6">
               <div className="p-4 border rounded-lg">
                 <SkeletonCanvas
                    sourceImage={imageFile || undefined}
                    analysisResult={analysisResult ? {
                      skeleton: analysisResult.edges_stats,
                      motifs: analysisResult.motifs,
                      intersections: analysisResult.intersections
                    } : undefined}
                  />
               </div>
               <div className="p-4 border rounded-lg space-y-4">
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <ResultsTable results={analysisResult?.metrics} />
                    <HistogramCard intersections={analysisResult?.intersections} />
                 </div>
                 <Button
                    variant="outline"
                    className="w-full"
                    disabled={!analysisResult || reportMutation.isPending}
                    onClick={() => reportMutation.mutate()}
                >
                    {reportMutation.isPending ? 'Generating Report...' : 'Download PDF Report'}
                </Button>
               </div>
            </div>
          </div>
        </main>
      </div>
    </ThemeProvider>
  );
}

// Final wrapper
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainApp />
    </QueryClientProvider>
  )
}

export default App;
