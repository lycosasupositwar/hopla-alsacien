import React from 'react';

const ResultsTable: React.FC = () => {
  return (
    <div>
      <h3>Metrics Summary</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b">
            <th className="text-left py-2">Metric</th>
            <th className="text-right py-2">Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="py-1">ASTM Grain Size (G)</td>
            <td className="text-right py-1 font-mono">-</td>
          </tr>
          <tr>
            <td className="py-1">Mean Intercept (µm)</td>
            <td className="text-right py-1 font-mono">-</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
