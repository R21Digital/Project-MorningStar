import React from 'react';

interface Boss {
  name: string;
  level: number;
  type: string;
  health: string;
  abilities: string[];
  tactics: string[];
  loot_table: string;
}

interface LootItem {
  item: string;
  rarity: string;
  slot: string;
  drop_rate?: number;
}

interface LootTable {
  guaranteed: LootItem[];
  random: LootItem[];
}

interface Strategy {
  name: string;
  description: string;
  tactics: string[];
}

interface HeroicData {
  name: string;
  slug: string;
  location: string;
  planet: string;
  coordinates: string;
  level_requirement: number;
  faction: string;
  group_size: string;
  difficulty: string;
  description: string;
  bosses: Boss[];
  trash_mobs: any[];
  loot_tables: Record<string, LootTable>;
  strategies: {
    general: string[];
    phase_1: Strategy;
    phase_2: Strategy;
    phase_3: Strategy;
  };
  requirements: string[];
  tips: string[];
  related_content: string[];
  last_updated: string;
  data_source: string;
}

interface HeroicDetailProps {
  heroic: HeroicData;
}

const HeroicDetail: React.FC<HeroicDetailProps> = ({ heroic }) => {
  const getRarityColor = (rarity: string) => {
    switch (rarity.toLowerCase()) {
      case 'epic':
        return 'text-purple-600';
      case 'rare':
        return 'text-blue-600';
      case 'uncommon':
        return 'text-green-600';
      case 'common':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="heroic-detail">
      {/* Header */}
      <div className="heroic-header mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">{heroic.name}</h1>
        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
            Level {heroic.level_requirement}+
          </span>
          <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
            {heroic.difficulty}
          </span>
          <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full">
            {heroic.group_size}
          </span>
          <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full">
            {heroic.planet}
          </span>
        </div>
      </div>

      {/* Description */}
      <div className="heroic-description mb-8">
        <p className="text-lg text-gray-700 leading-relaxed">{heroic.description}</p>
      </div>

      {/* Location Info */}
      <div className="location-info mb-8 p-6 bg-gray-50 rounded-lg">
        <h2 className="text-2xl font-semibold mb-4">Location</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <strong>Planet:</strong> {heroic.planet}
          </div>
          <div>
            <strong>Location:</strong> {heroic.location}
          </div>
          <div>
            <strong>Coordinates:</strong> {heroic.coordinates}
          </div>
          <div>
            <strong>Faction:</strong> {heroic.faction}
          </div>
        </div>
      </div>

      {/* Bosses */}
      <div className="bosses-section mb-8">
        <h2 className="text-2xl font-semibold mb-6">Bosses</h2>
        <div className="space-y-6">
          {heroic.bosses.map((boss, index) => (
            <div key={index} className="boss-card p-6 border border-gray-200 rounded-lg">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold text-red-600">{boss.name}</h3>
                <div className="flex gap-2">
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                    Level {boss.level}
                  </span>
                  <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                    {boss.type}
                  </span>
                  <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                    {boss.health}
                  </span>
                </div>
              </div>

              {/* Abilities */}
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Abilities:</h4>
                <div className="flex flex-wrap gap-2">
                  {boss.abilities.map((ability, idx) => (
                    <span key={idx} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                      {ability}
                    </span>
                  ))}
                </div>
              </div>

              {/* Tactics */}
              <div>
                <h4 className="font-semibold mb-2">Tactics:</h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                  {boss.tactics.map((tactic, idx) => (
                    <li key={idx}>{tactic}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Loot Tables */}
      <div className="loot-tables-section mb-8">
        <h2 className="text-2xl font-semibold mb-6">Loot Tables</h2>
        <div className="space-y-6">
          {Object.entries(heroic.loot_tables).map(([tableName, lootTable]) => (
            <div key={tableName} className="loot-table-card p-6 border border-gray-200 rounded-lg">
              <h3 className="text-lg font-semibold mb-4 capitalize">
                {tableName.replace(/_/g, ' ')}
              </h3>

              {/* Guaranteed Loot */}
              {lootTable.guaranteed.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-semibold mb-2 text-green-600">Guaranteed Drops:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {lootTable.guaranteed.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center p-2 bg-green-50 rounded">
                        <span className="font-medium">{item.item}</span>
                        <div className="flex gap-2 text-sm">
                          <span className={getRarityColor(item.rarity)}>{item.rarity}</span>
                          <span className="text-gray-500">{item.slot}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Random Loot */}
              {lootTable.random.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 text-blue-600">Random Drops:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {lootTable.random.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center p-2 bg-blue-50 rounded">
                        <span className="font-medium">{item.item}</span>
                        <div className="flex gap-2 text-sm">
                          <span className={getRarityColor(item.rarity)}>{item.rarity}</span>
                          <span className="text-gray-500">{item.slot}</span>
                          {item.drop_rate && (
                            <span className="text-orange-600">{(item.drop_rate * 100).toFixed(1)}%</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Strategies */}
      <div className="strategies-section mb-8">
        <h2 className="text-2xl font-semibold mb-6">Strategies</h2>
        
        {/* General Strategies */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">General Tips:</h3>
          <ul className="list-disc list-inside space-y-1 text-gray-700">
            {heroic.strategies.general.map((strategy, idx) => (
              <li key={idx}>{strategy}</li>
            ))}
          </ul>
        </div>

        {/* Phase Strategies */}
        <div className="space-y-6">
          {Object.entries(heroic.strategies).filter(([key]) => key.startsWith('phase_')).map(([phaseKey, strategy]) => (
            <div key={phaseKey} className="phase-strategy p-4 border border-gray-200 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">{strategy.name}</h3>
              <p className="text-gray-600 mb-3">{strategy.description}</p>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                {strategy.tactics.map((tactic, idx) => (
                  <li key={idx}>{tactic}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Requirements */}
      <div className="requirements-section mb-8">
        <h2 className="text-2xl font-semibold mb-4">Requirements</h2>
        <ul className="list-disc list-inside space-y-1 text-gray-700">
          {heroic.requirements.map((requirement, idx) => (
            <li key={idx}>{requirement}</li>
          ))}
        </ul>
      </div>

      {/* Tips */}
      <div className="tips-section mb-8">
        <h2 className="text-2xl font-semibold mb-4">Tips & Tricks</h2>
        <ul className="list-disc list-inside space-y-1 text-gray-700">
          {heroic.tips.map((tip, idx) => (
            <li key={idx}>{tip}</li>
          ))}
        </ul>
      </div>

      {/* Related Content */}
      <div className="related-content-section mb-8">
        <h2 className="text-2xl font-semibold mb-4">Related Content</h2>
        <div className="flex flex-wrap gap-2">
          {heroic.related_content.map((content, idx) => (
            <span key={idx} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
              {content}
            </span>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="heroic-footer text-sm text-gray-500 border-t pt-4">
        <div className="flex justify-between items-center">
          <span>Last updated: {heroic.last_updated}</span>
          <span>Data source: {heroic.data_source}</span>
        </div>
      </div>
    </div>
  );
};

export default HeroicDetail; 