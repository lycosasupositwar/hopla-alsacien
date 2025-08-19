import React from 'react';

const PreprocessPanel: React.FC = () => {
  return (
    <div>
      <h3>Preprocessing Parameters</h3>
      <div className="space-y-4">
        <div>
          <label htmlFor="gaussian_sigma" className="text-sm font-medium">Gaussian Sigma</label>
          {/* Slider will replace this input */}
          <input type="range" id="gaussian_sigma" min="0" max="5" step="0.1" className="w-full" />
        </div>
        <div>
          <label htmlFor="adaptive_block_size" className="text-sm font-medium">Adaptive Block Size</label>
          {/* Slider will replace this input */}
          <input type="range" id="adaptive_block_size" min="3" max="201" step="2" className="w-full" />
        </div>
        <div>
          <label htmlFor="adaptive_offset" className="text-sm font-medium">Adaptive Offset</label>
          {/* Slider will replace this input */}
          <input type="range" id="adaptive_offset" min="0" max="20" step="1" className="w-full" />
        </div>
      </div>
    </div>
  );
};

export default PreprocessPanel;
