import React from 'react';

const ImageUploader: React.FC = () => {
  return (
    <div>
      <h3>Image Uploader</h3>
      {/* Drag and drop area will be implemented here */}
      <div className="p-10 border-2 border-dashed rounded-lg text-center">
        <p>Drag 'n' drop an image here, or click to select a file</p>
      </div>
    </div>
  );
};

export default ImageUploader;
