import React from 'react';

export default function BuildSnapshot({ build }) {
  const formatNumber = (num) => {
    return num.toLocaleString();
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
      <h3 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center">
        <i className="fas fa-chart-bar mr-2"></i>
        Build Summary
      </h3>
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-gray-700 p-2 rounded">
          <div className="text-gray-400 text-xs uppercase tracking-wide">Skill Points</div>
          <div className="text-white font-semibold">{build.pointsUsed || 0} / 250</div>
        </div>
        <div className="bg-gray-700 p-2 rounded">
          <div className="text-gray-400 text-xs uppercase tracking-wide">XP Required</div>
          <div className="text-white font-semibold">{formatNumber(build.totalXP || 0)}</div>
        </div>
        <div className="bg-gray-700 p-2 rounded">
          <div className="text-gray-400 text-xs uppercase tracking-wide">Skills Selected</div>
          <div className="text-white font-semibold">{build.skills ? build.skills.length : 0}</div>
        </div>
        <div className="bg-gray-700 p-2 rounded">
          <div className="text-gray-400 text-xs uppercase tracking-wide">Profession</div>
          <div className="text-white font-semibold">{build.profession || 'None'}</div>
        </div>
      </div>
      
      {build.skills && build.skills.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="text-gray-400 text-xs uppercase tracking-wide mb-2">Selected Skills</div>
          <div className="text-xs text-gray-300 max-h-20 overflow-y-auto">
            {build.skills.slice(0, 5).join(', ')}
            {build.skills.length > 5 && ` +${build.skills.length - 5} more`}
          </div>
        </div>
      )}
    </div>
  );
}
