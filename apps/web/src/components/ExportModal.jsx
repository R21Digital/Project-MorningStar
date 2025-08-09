import React from 'react';
import { encodeBuildToURL, downloadBuildAsJSON } from '../utils/exportBuild';
import BuildSnapshot from './BuildSnapshot';

export default function ExportModal({ buildData, onClose }) {
  const url = encodeBuildToURL(buildData);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(url).then(() => {
      // Show success feedback
      const button = document.getElementById('copy-url-btn');
      const originalText = button.innerHTML;
      button.innerHTML = '<i class="fas fa-check mr-2"></i>Copied!';
      button.className = 'flex-1 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-semibold transition-colors';
      setTimeout(() => {
        button.innerHTML = originalText;
        button.className = 'flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-semibold transition-colors';
      }, 2000);
    }).catch(() => {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = url;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      
      const button = document.getElementById('copy-url-btn');
      const originalText = button.innerHTML;
      button.innerHTML = '<i class="fas fa-check mr-2"></i>Copied!';
      button.className = 'flex-1 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-semibold transition-colors';
      setTimeout(() => {
        button.innerHTML = originalText;
        button.className = 'flex-1 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-semibold transition-colors';
      }, 2000);
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-70 backdrop-blur-sm">
      <div className="bg-gray-900 text-white rounded-lg p-6 max-w-md w-full shadow-xl border border-cyan-500 relative mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-cyan-400">Export Build</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <i className="fas fa-times text-xl"></i>
          </button>
        </div>
        
        <p className="text-sm mb-4 text-gray-300">Use the options below to share or save your build.</p>

        <BuildSnapshot build={buildData} />

        <div className="mt-4">
          <label className="block text-sm font-medium mb-2 text-cyan-400">Sharable URL</label>
          <div className="flex">
            <input
              type="text"
              value={url}
              readOnly
              onClick={(e) => e.target.select()}
              className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-l text-sm focus:border-cyan-500 focus:outline-none"
            />
            <button
              id="copy-url-btn"
              onClick={copyToClipboard}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-r text-sm font-semibold transition-colors border border-blue-600"
            >
              <i class="fas fa-copy mr-1"></i>Copy
            </button>
          </div>
        </div>

        <div className="flex justify-between mt-6 space-x-3">
          <button
            className="flex-1 py-3 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-semibold transition-colors border border-green-600 hover:border-green-700"
            onClick={() => downloadBuildAsJSON(buildData)}
          >
            <i className="fas fa-download mr-2"></i>
            Download JSON
          </button>
          <button
            className="flex-1 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-semibold transition-colors border border-gray-600 hover:border-gray-500"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
