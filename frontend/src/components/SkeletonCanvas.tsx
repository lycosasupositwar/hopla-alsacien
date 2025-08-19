import React, { useState, useEffect, useRef } from 'react';
import { Stage, Layer, Image as KonvaImage, Line, Circle } from 'react-konva';
import Konva from 'konva';

// A placeholder image for initial display
const PLACEHOLDER_IMG_URL = "https://via.placeholder.com/800x600.png?text=Upload+an+image+to+start";

// Define props for the component
interface SkeletonCanvasProps {
    sourceImage?: File; // The uploaded image file
    // We will add skeleton, motifs, and intersection data as props later
}

const SkeletonCanvas: React.FC<SkeletonCanvasProps> = ({ sourceImage }) => {
    const [image, setImage] = useState<HTMLImageElement | null>(null);
    const [stagePos, setStagePos] = useState({ x: 0, y: 0 });
    const [stageScale, setStageScale] = useState(1);
    const containerRef = useRef<HTMLDivElement>(null);

    // Effect to load the image from a File or URL
    useEffect(() => {
        const img = new window.Image();
        if (sourceImage) {
            img.src = URL.createObjectURL(sourceImage);
        } else {
            img.src = PLACEHOLDER_IMG_URL;
        }
        img.onload = () => {
            setImage(img);
            // Center the image on load
            if(containerRef.current) {
                const { width, height } = containerRef.current.getBoundingClientRect();
                setStageScale(Math.min(width / img.width, height / img.height) * 0.9);
            }
        };
    }, [sourceImage]);

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

    const handleDragEnd = (e: Konva.KonvaEventObject<DragEvent>) => {
        setStagePos(e.target.position());
    };

    const containerSize = containerRef.current ? containerRef.current.getBoundingClientRect() : { width: 0, height: 0};

    return (
        <div ref={containerRef} className="w-full h-96 bg-muted rounded-lg overflow-hidden">
            {containerSize.width > 0 && (
                 <Stage
                    width={containerSize.width}
                    height={containerSize.height}
                    onWheel={handleWheel}
                    scaleX={stageScale}
                    scaleY={stageScale}
                    x={stagePos.x}
                    y={stagePos.y}
                    draggable
                    onDragEnd={handleDragEnd}
                >
                    <Layer>
                        {image && <KonvaImage image={image} />}
                    </Layer>
                    {/* Skeleton Layer */}
                    <Layer>
                        {/* Skeleton lines will be rendered here */}
                    </Layer>
                    {/* Motif Layer */}
                    <Layer>
                        {/* Motif lines/circles will be rendered here */}
                    </Layer>
                    {/* Intersection Layer */}
                    <Layer>
                        {/* Intersection points will be rendered here */}
                    </Layer>
                </Stage>
            )}
        </div>
    );
};

export default SkeletonCanvas;
