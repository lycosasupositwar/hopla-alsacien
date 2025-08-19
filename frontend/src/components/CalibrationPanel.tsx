import React from 'react';

const CalibrationPanel: React.FC = () => {
  return (
    <div>
      <h3>Calibration</h3>
      <div className="space-y-2">
        <div>
          <label htmlFor="pixel_size" className="text-sm font-medium">Pixel Size (µm/px)</label>
          <input type="number" id="pixel_size" className="w-full p-2 border rounded-md bg-input" placeholder="e.g., 0.5" />
        </div>
        <p className="text-xs text-center text-muted-foreground">or</p>
        <div>
          <label htmlFor="magnification" className="text-sm font-medium">Magnification</label>
          <input type="number" id="magnification" className="w-full p-2 border rounded-md bg-input" placeholder="e.g., 100" />
        </div>
      </div>
    </div>
  );
};

export default CalibrationPanel;
