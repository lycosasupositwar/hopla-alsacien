import { useState } from "react";
import { Button } from "@/components/ui/button"; // Button exists, so I can keep it.
import { fetchLogs } from "@/lib/api";

export const LogsPanel = () => {
  const [logs, setLogs] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetchLogs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const logsData = await fetchLogs();
      const formattedLogs = Object.entries(logsData)
        .map(([fileName, content]) => `--- ${fileName} ---\n\n${content}`)
        .join("\n\n\n");
      setLogs(formattedLogs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
      setLogs(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-card text-card-foreground shadow-sm">
      <div className="flex flex-col space-y-1.5 p-6">
         <h3 className="font-semibold leading-none tracking-tight">Container Logs</h3>
      </div>
      <div className="p-6 pt-0">
        <div className="flex flex-col gap-4">
          <Button onClick={handleFetchLogs} disabled={isLoading}>
            {isLoading ? "Loading..." : "Fetch Logs"}
          </Button>
          {error && <p className="text-red-500">{error}</p>}
          {logs !== null && (
            <textarea
              readOnly
              value={logs}
              className="mt-2 flex h-96 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 font-mono text-xs"
              placeholder="Logs will appear here..."
            />
          )}
        </div>
      </div>
    </div>
  );
};
