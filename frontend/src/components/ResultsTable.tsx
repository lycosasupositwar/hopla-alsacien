import React from 'react';

interface ResultsTableProps {
    results?: {
        G: number;
        ell_um: number;
        ell_mm: number;
        N_int: number;
    } | null;
}

const ResultsTable: React.FC<ResultsTableProps> = ({ results }) => {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Metrics Summary</h3>
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
            <td className="text-right py-1 font-mono">{results ? results.G.toFixed(3) : '-'}</td>
          </tr>
          <tr>
            <td className="py-1">Mean Intercept (µm)</td>
            <td className="text-right py-1 font-mono">{results ? results.ell_um.toFixed(2) : '-'}</td>
          </tr>
          <tr>
            <td className="py-1">Mean Intercept (mm)</td>
            <td className="text-right py-1 font-mono">{results ? results.ell_mm.toFixed(5) : '-'}</td>
          </tr>
          <tr>
            <td className="py-1">Weighted Intersections</td>
            <td className="text-right py-1 font-mono">{results ? results.N_int.toFixed(1) : '-'}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default ResultsTable;
