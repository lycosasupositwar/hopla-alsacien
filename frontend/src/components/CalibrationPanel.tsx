import React from 'react';

interface CalibrationPanelProps {
    onPixelSizeChange: (value: number) => void;
}

const CalibrationPanel: React.FC<CalibrationPanelProps> = ({ onPixelSizeChange }) => {
  return (
    <div className="mt-4">
      <h3 className="text-lg font-semibold mb-2">2. Calibration</h3>
      <div className="space-y-2">
        <div>
          <label htmlFor="pixel_size" className="text-sm font-medium">Pixel Size (µm/px)</label>
          <input
            type="number"
            id="pixel_size"
            className="w-full p-2 border rounded-md bg-input"
            placeholder="e.g., 0.5"
            step="0.01"
            onChange={(e) => onPixelSizeChange(parseFloat(e.target.value) || 0)}
          />
        </div>
        {/* The logic for converting magnification to pixel size would be added here */}
      </div>
    </div>
  );
};

export default CalibrationPanel;
