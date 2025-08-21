import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { fetchLogs } from "@/lib/api";

export const LogsPanel = () => {
  const [logs, setLogs] = useState<Record<string, string> | null>(null);
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
      setLogs({ formatted: formattedLogs });
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
      setLogs(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Container Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-4">
          <Button onClick={handleFetchLogs} disabled={isLoading}>
            {isLoading ? "Loading..." : "Fetch Logs"}
          </Button>
          {error && <p className="text-red-500">{error}</p>}
          {logs && (
            <Textarea
              readOnly
              value={logs.formatted}
              className="h-96 font-mono text-xs"
              placeholder="Logs will appear here..."
            />
          )}
        </div>
      </CardContent>
    </Card>
  );
};
