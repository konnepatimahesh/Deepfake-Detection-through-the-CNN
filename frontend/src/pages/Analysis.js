import React, { useState } from 'react';
import { detectionAPI } from '../services/api';
import Loader from '../components/Loader';

const Analysis = () => {
  const [file, setFile] = useState(null);
  const [fileType, setFileType] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    if (!selectedFile) return;

    setError('');
    setResult(null);

    const type = selectedFile.type.startsWith('image/') ? 'image' : 
                 selectedFile.type.startsWith('video/') ? 'video' : null;

    if (!type) {
      setError('Please upload an image or video file');
      return;
    }

    if (selectedFile.size > 100 * 1024 * 1024) {
      setError('File size must be less than 100MB');
      return;
    }

    setFile(selectedFile);
    setFileType(type);

    if (type === 'image') {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      let response;
      if (fileType === 'image') {
        response = await detectionAPI.analyzeImage(formData);
      } else {
        response = await detectionAPI.analyzeVideo(formData);
      }

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setFileType(null);
    setPreview(null);
    setResult(null);
    setError('');
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Deepfake Detection Analysis
          </h1>
          <p className="text-gray-600 mb-8">
            Upload an image or video to detect potential deepfakes using AI
          </p>

          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select File
            </label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                {preview ? (
                  <img src={preview} alt="Preview" className="max-h-60 rounded" />
                ) : (
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <svg className="w-12 h-12 mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="mb-2 text-sm text-gray-500">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500">
                      Images (PNG, JPG, GIF) or Videos (MP4, AVI, MOV)
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Max size: 100MB</p>
                  </div>
                )}
                <input
                  type="file"
                  className="hidden"
                  accept="image/*,video/*"
                  onChange={handleFileChange}
                />
              </label>
            </div>

            {file && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-900">Selected File:</p>
                    <p className="text-sm text-blue-700">{file.name}</p>
                    <p className="text-xs text-blue-600">
                      Type: {fileType} | Size: {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={handleReset}
                    className="text-red-600 hover:text-red-800"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="mb-6 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Analyzing...' : 'Analyze File'}
          </button>

          {loading && (
            <div className="mt-8">
              <Loader message={`Analyzing ${fileType}... This may take a moment.`} />
            </div>
          )}

          {result && (
            <div className="mt-8 border-t pt-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Analysis Results</h2>

              <div className={`p-6 rounded-lg mb-6 ${
                result.prediction === 'fake' ? 'bg-red-50 border-2 border-red-200' : 'bg-green-50 border-2 border-green-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold">
                      {result.prediction === 'fake' ? '⚠️ Deepfake Detected' : '✅ Authentic Content'}
                    </h3>
                    <p className="text-sm mt-1">
                      Confidence: <span className="font-bold">{result.confidence}%</span>
                    </p>
                  </div>
                  <div className={`text-6xl ${result.prediction === 'fake' ? 'text-red-500' : 'text-green-500'}`}>
                    {result.prediction === 'fake' ? '🚨' : '✓'}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">File Name</p>
                  <p className="font-semibold">{result.file_name}</p>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">File Size</p>
                  <p className="font-semibold">{result.file_size_mb} MB</p>
                </div>

                {result.face_count !== undefined && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Faces Detected</p>
                    <p className="font-semibold">{result.face_count}</p>
                  </div>
                )}

                {result.frames_analyzed && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Frames Analyzed</p>
                    <p className="font-semibold">{result.frames_analyzed}</p>
                  </div>
                )}

                {result.video_info && (
                  <>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Duration</p>
                      <p className="font-semibold">{result.video_info.duration_formatted}</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm text-gray-600">Resolution</p>
                      <p className="font-semibold">{result.video_info.width}x{result.video_info.height}</p>
                    </div>
                  </>
                )}
              </div>

              {result.quality_metrics && (
                <div className="mt-6 bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Quality Metrics</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>Blur Score: {result.quality_metrics.blur_score?.toFixed(2)}</div>
                    <div>Brightness: {result.quality_metrics.brightness?.toFixed(2)}</div>
                    {result.quality_metrics.is_blurry && (
                      <div className="col-span-2 text-yellow-600">
                        ⚠️ Image appears blurry - may affect accuracy
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="mt-6 flex gap-4">
                <button
                  onClick={handleReset}
                  className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700"
                >
                  Analyze Another File
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analysis;