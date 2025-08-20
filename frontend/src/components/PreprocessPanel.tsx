import React from 'react';
import { Button } from '@/components/ui/button';

interface PreprocessPanelProps {
    params: { [key: string]: any };
    onParamsChange: (newParams: { [key: string]: any }) => void;
    onPreview: () => void;
    isImageLoaded: boolean;
    isPreviewing: boolean;
}

const PreprocessPanel: React.FC<PreprocessPanelProps> = ({ params, onParamsChange, onPreview, isImageLoaded, isPreviewing }) => {

    const handleParamChange = (key: string, value: number) => {
        onParamsChange({ ...params, [key]: value });
    };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">2. Preprocessing Parameters</h3>
      <div className="space-y-4">
        <div>
          <label htmlFor="gaussian_sigma" className="flex justify-between text-sm font-medium">
            <span>Gaussian Sigma</span>
            <span>{params.gaussian_sigma}</span>
          </label>
          <input
            type="range" id="gaussian_sigma"
            min="0.1" max="5" step="0.1"
            value={params.gaussian_sigma}
            onChange={(e) => handleParamChange('gaussian_sigma', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
        <div>
          <label htmlFor="adaptive_block_size" className="flex justify-between text-sm font-medium">
            <span>Adaptive Block Size</span>
            <span>{params.adaptive_block_size}</span>
          </label>
          <input
            type="range" id="adaptive_block_size"
            min="3" max="201" step="2"
            value={params.adaptive_block_size}
            onChange={(e) => handleParamChange('adaptive_block_size', parseInt(e.target.value))}
            className="w-full"
          />
        </div>
        <div>
          <label htmlFor="adaptive_offset" className="flex justify-between text-sm font-medium">
            <span>Adaptive Offset</span>
            <span>{params.adaptive_offset}</span>
          </label>
          <input
            type="range" id="adaptive_offset"
            min="0" max="20" step="1"
            value={params.adaptive_offset}
            onChange={(e) => handleParamChange('adaptive_offset', parseInt(e.target.value))}
            className="w-full"
         />
        </div>
      </div>
      <Button
        variant="outline"
        className="w-full mt-4"
        onClick={onPreview}
        disabled={!isImageLoaded || isPreviewing}
      >
        {isPreviewing ? 'Loading Preview...' : 'Preview Preprocessing'}
      </Button>
    </div>
  );
};

export default PreprocessPanel;
