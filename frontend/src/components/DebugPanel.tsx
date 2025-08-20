import React from 'react';

// Define the type for the debug overlays prop
interface DebugOverlays {
    binary_image_base64: string;
    skeleton_image_base64: string;
}

interface DebugPanelProps {
    debugData?: DebugOverlays | null;
}

const DebugPanel: React.FC<DebugPanelProps> = ({ debugData }) => {
    if (!debugData) {
        return null; // Don't render anything if there's no debug data
    }

    return (
        <div className="p-4 border rounded-lg mt-6">
            <h2 className="text-lg font-semibold mb-4">Debugging Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <h3 className="text-md font-medium text-center mb-2">Preprocessing Result (Binary)</h3>
                    <img
                        src={debugData.binary_image_base64}
                        alt="Preprocessing Result"
                        className="w-full h-auto border rounded-md"
                    />
                </div>
                <div>
                    <h3 className="text-md font-medium text-center mb-2">Raw Skeleton</h3>
                    <img
                        src={debugData.skeleton_image_base64}
                        alt="Raw Skeleton"
                        className="w-full h-auto border rounded-md"
                    />
                </div>
            </div>
        </div>
    );
};

export default DebugPanel;
