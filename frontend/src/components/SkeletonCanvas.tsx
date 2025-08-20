import React, { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Image as KonvaImage, Line, Circle } from 'react-konva';
import Konva from 'konva';

// Type definitions for the analysis data, mirroring the backend schemas
// These would typically be in a shared types file.
interface Intersection {
    id: number;
    x: number;
    y: number;
    type: 'jonction' | 'régulière' | 'extrémité';
    score: number;
}

interface Motif {
    id: string;
    type: string;
    geometry: { coordinates: [number, number][] }; // Simplified for rendering
    length_px: number;
}

interface SkeletonData {
    // For simplicity, we'll assume the skeleton is passed as a list of polylines
    edges: { coords: [number, number][] }[];
}

interface AnalysisResult {
    // This will eventually hold the full result from the backend
    skeleton: SkeletonData;
    motifs: Motif[];
    intersections: Intersection[];
}


interface SkeletonCanvasProps {
    sourceImage?: File;
    previewImage?: string | null;
    analysisResult?: AnalysisResult | null; // The full analysis result from the backend
}

const SkeletonCanvas: React.FC<SkeletonCanvasProps> = ({ sourceImage, previewImage, analysisResult }) => {
    const [image, setImage] = useState<HTMLImageElement | null>(null);
    const [stagePos, setStagePos] = useState({ x: 0, y: 0 });
    const [stageScale, setStageScale] = useState(1);
    const [layerVisibility, setLayerVisibility] = useState({
        skeleton: true,
        motifs: true,
        intersections: true,
    });
    const containerRef = useRef<HTMLDivElement>(null);

    // Effect to load the source or preview image and reset the view
    useEffect(() => {
        const img = new window.Image();
        let objectUrl: string | null = null;

        if (previewImage) {
            img.src = previewImage;
        } else if (sourceImage) {
            objectUrl = URL.createObjectURL(sourceImage);
            img.src = objectUrl;
        } else {
            setImage(null);
            return;
        }

        img.onload = () => {
            setImage(img);
            if (containerRef.current) {
                const { width, height } = containerRef.current.getBoundingClientRect();
                const scale = Math.min(width / img.width, height / img.height) * 0.95;
                setStageScale(scale);
                setStagePos({
                    x: (width - img.width * scale) / 2,
                    y: (height - img.height * scale) / 2,
                });
            }
        };

        // Cleanup function to revoke the object URL if it was created
        return () => {
            if (objectUrl) {
                URL.revokeObjectURL(objectUrl);
            }
        };
    }, [sourceImage, previewImage]);

    const handleWheel = (e: Konva.KonvaEventObject<WheelEvent>) => {
        e.evt.preventDefault();
        const scaleBy = 1.1;
        const stage = e.target.getStage();
        if (!stage) return;

        const oldScale = stage.scaleX();
        const pointer = stage.getPointerPosition();
        if (!pointer) return;

        const mousePointTo = {
            x: (pointer.x - stage.x()) / oldScale,
            y: (pointer.y - stage.y()) / oldScale,
        };

        const newScale = e.evt.deltaY > 0 ? oldScale / scaleBy : oldScale * scaleBy;
        setStageScale(newScale);

        const newPos = {
            x: pointer.x - mousePointTo.x * newScale,
            y: pointer.y - mousePointTo.y * newScale,
        };
        setStagePos(newPos);
    };

    const intersectionColorMap = {
        jonction: "#ef4444", // red-500
        régulière: "#eab308", // yellow-500
        extrémité: "#3b82f6", // blue-500
    };

    const containerSize = containerRef.current ? containerRef.current.getBoundingClientRect() : { width: 0, height: 0};

    return (
        <div>
            <div ref={containerRef} className="w-full h-[500px] bg-muted rounded-lg overflow-hidden border flex items-center justify-center">
                {(sourceImage || previewImage) && image && containerSize.width > 0 ? (
                     <Stage
                        width={containerSize.width}
                        height={containerSize.height}
                        onWheel={handleWheel}
                        scaleX={stageScale}
                        scaleY={stageScale}
                        x={stagePos.x}
                        y={stagePos.y}
                        draggable
                        onDragEnd={(e) => setStagePos(e.target.position())}
                    >
                        <Layer>
                            <KonvaImage image={image} />
                        </Layer>

                        {/* Analysis overlays should only be visible when not in preview mode */}
                        {!previewImage && (
                            <>
                                <Layer visible={layerVisibility.skeleton}>
                                    {analysisResult?.skeleton.edges.map((edge, i) => (
                                        <Line key={`skel-${i}`} points={edge.coords.flat()} stroke="green" strokeWidth={1 / stageScale} />
                                    ))}
                                </Layer>

                                <Layer visible={layerVisibility.motifs}>
                                    {analysisResult?.motifs.map((motif, i) => (
                                        <Line key={`motif-${i}`} points={motif.geometry.coordinates.flat()} stroke="blue" strokeWidth={2 / stageScale} />
                                    ))}
                                </Layer>

                                <Layer visible={layerVisibility.intersections}>
                                    {analysisResult?.intersections.map((inter) => (
                                        <Circle
                                            key={`inter-${inter.id}`}
                                            x={inter.x}
                                            y={inter.y}
                                            radius={5 / stageScale}
                                            fill={intersectionColorMap[inter.type]}
                                            stroke="black"
                                            strokeWidth={1 / stageScale}
                                        />
                                    ))}
                                </Layer>
                            </>
                        )}
                    </Stage>
                ) : (
                    <div className="text-center text-muted-foreground p-4">
                        <p className="font-semibold">Upload an image to start</p>
                        <p className="text-sm">The analysis canvas will appear here.</p>
                    </div>
                )}
            </div>
            <div className="flex items-center space-x-4 mt-2">
                <p className="text-sm font-semibold">Overlays:</p>
                {Object.keys(layerVisibility).map((key) => (
                    <label key={key} className="flex items-center space-x-2 text-sm cursor-pointer">
                        <input
                            type="checkbox"
                            checked={layerVisibility[key as keyof typeof layerVisibility]}
                            onChange={(e) => setLayerVisibility({...layerVisibility, [key]: e.target.checked})}
                            className="form-checkbox h-4 w-4 rounded"
                        />
                        <span>{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                    </label>
                ))}
            </div>
        </div>
    );
};

export default SkeletonCanvas;
