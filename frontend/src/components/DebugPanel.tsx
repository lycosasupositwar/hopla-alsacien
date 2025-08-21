import React from 'react';

import React from 'react';

// Define the types for the debug data props
interface DebugOverlays {
    binary_image_base64: string;
    skeleton_image_base64: string;
}

interface DebugStats {
    nodes_before_pruning: number;
    edges_before_pruning: number;
    nodes_after_pruning: number;
    edges_after_pruning: number;
    edge_geometries_count: number;
}

interface DebugPanelProps {
    debugOverlays?: DebugOverlays | null;
    debugStats?: DebugStats | null;
}

const DebugPanel: React.FC<DebugPanelProps> = ({ debugOverlays, debugStats }) => {
    if (!debugOverlays && !debugStats) {
        return null; // Don't render anything if there's no debug data
    }

    return (
        <div className="p-4 border rounded-lg mt-6">
            <h2 className="text-lg font-semibold mb-4">Debugging Information</h2>

            {/* Graph Stats Console */}
            {debugStats && (
                <div className="mb-4 p-3 bg-muted/50 rounded-lg">
                    <h3 className="text-md font-medium mb-2">Graph Processing Log</h3>
                    <ul className="text-sm font-mono space-y-1">
                        <li>Nodes before pruning: {debugStats.nodes_before_pruning}</li>
                        <li>Edges before pruning: {debugStats.edges_before_pruning}</li>
                        <li className="pt-1 border-t border-muted-foreground/20">Nodes after pruning:  {debugStats.nodes_after_pruning}</li>
                        <li>Edges after pruning:  {debugStats.edges_after_pruning}</li>
                        <li className="pt-1 border-t border-destructive/20 text-destructive">Edges sent to frontend: {debugStats.edge_geometries_count}</li>
                    </ul>
                </div>
            )}

            {/* Image Overlays */}
            {debugOverlays && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h3 className="text-md font-medium text-center mb-2">Preprocessing Result (Binary)</h3>
                        <img
                            src={debugOverlays.binary_image_base64}
                            alt="Preprocessing Result"
                            className="w-full h-auto border rounded-md"
                        />
                    </div>
                    <div>
                        <h3 className="text-md font-medium text-center mb-2">Raw Skeleton</h3>
                        <img
                            src={debugOverlays.skeleton_image_base64}
                            alt="Raw Skeleton"
                            className="w-full h-auto border rounded-md"
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default DebugPanel;
