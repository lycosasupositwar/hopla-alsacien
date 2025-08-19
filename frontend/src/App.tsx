import { ThemeProvider } from "@/components/theme-provider"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import ImageUploader from "./components/ImageUploader"
import CalibrationPanel from "./components/CalibrationPanel"
import PreprocessPanel from "./components/PreprocessPanel"
import SkeletonCanvas from "./components/SkeletonCanvas"
import ResultsTable from "./components/ResultsTable"
import HistogramCard from "./components/HistogramCard"

// Create a client
const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
        <div className="min-h-screen bg-background text-foreground">
          <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 items-center">
              <h1 className="text-xl font-bold">Automated Grain Size Analysis</h1>
            </div>
          </header>

          <main className="container mx-auto p-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Controls */}
              <div className="lg:col-span-1 space-y-6">
                <div className="p-4 border rounded-lg">
                  <ImageUploader />
                  <CalibrationPanel />
                </div>
                <div className="p-4 border rounded-lg">
                  <PreprocessPanel />
                </div>
                 <div className="p-4 border rounded-lg">
                  <h2 className="text-lg font-semibold mb-2">3. Analysis & Motifs</h2>
                  <p className="text-sm text-muted-foreground">MotifGenerator will go here.</p>
                  <button className="w-full p-2 mt-4 bg-primary text-primary-foreground rounded-md">Analyze</button>
                </div>
              </div>

              {/* Right Column: Canvas & Results */}
              <div className="lg:col-span-2 space-y-6">
                 <div className="p-4 border rounded-lg">
                   <SkeletonCanvas />
                 </div>
                 <div className="p-4 border rounded-lg grid grid-cols-1 md:grid-cols-2 gap-4">
                   <ResultsTable />
                   <HistogramCard />
                 </div>
              </div>
            </div>
          </main>
        </div>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
