import React, { useState } from 'react';
import ExportModal from './ExportModal';

export default function ExportBuildButton({ buildData }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-4 right-4 z-50 px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold shadow-lg hover:scale-105 transition-all duration-300 hover:shadow-cyan-500/25 border border-cyan-400/50"
      >
        <i className="fas fa-download mr-2"></i>
        Export Build
      </button>
      {open && <ExportModal buildData={buildData} onClose={() => setOpen(false)} />}
    </>
  );
}
