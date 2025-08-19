import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface Intersection {
    type: string;
}

interface HistogramCardProps {
    intersections?: Intersection[] | null;
}

const HistogramCard: React.FC<HistogramCardProps> = ({ intersections }) => {
    const processData = () => {
        if (!intersections) return [];
        const counts = intersections.reduce((acc, curr) => {
            acc[curr.type] = (acc[curr.type] || 0) + 1;
            return acc;
        }, {} as Record<string, number>);

        return Object.keys(counts).map(key => ({
            name: key.charAt(0).toUpperCase() + key.slice(1),
            count: counts[key],
        }));
    };

    const data = processData();

  return (
    <div>
      <h3 className="text-lg font-semibold mb-2">Intersection Types</h3>
      <div className="w-full h-48 rounded-lg">
        {intersections && intersections.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis allowDecimals={false} />
                    <Tooltip cursor={{fill: 'rgba(128,128,128,0.1)'}}/>
                    <Legend />
                    <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
            </ResponsiveContainer>
        ) : (
             <div className="w-full h-full bg-muted rounded-lg flex items-center justify-center">
                <p className="text-sm text-muted-foreground">No intersection data</p>
            </div>
        )}
      </div>
    </div>
  );
};

export default HistogramCard;
