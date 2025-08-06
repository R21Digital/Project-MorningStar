import React, { useState, useEffect } from 'react';
import './MacroBuilder.css';

interface MacroAction {
  id: string;
  type: 'command' | 'pause' | 'loop' | 'condition' | 'variable' | 'comment';
  command: string;
  parameters: Record<string, any>;
  delay_ms: number;
  description: string;
  is_conditional: boolean;
  condition?: string;
}

interface MacroDefinition {
  name: string;
  description: string;
  author: string;
  category: string;
  tags: string[];
  actions: MacroAction[];
  variables: Record<string, any>;
  settings: Record<string, any>;
  is_public: boolean;
}

interface MacroBuilderProps {
  onMacroSave?: (macro: MacroDefinition) => void;
  onMacroTest?: (macroText: string) => void;
  onMacroLoad?: (name: string) => void;
}

const MacroBuilder: React.FC<MacroBuilderProps> = ({
  onMacroSave,
  onMacroTest,
  onMacroLoad
}) => {
  const [activeTab, setActiveTab] = useState<'builder' | 'library' | 'import' | 'settings'>('builder');
  const [macroName, setMacroName] = useState('');
  const [macroDescription, setMacroDescription] = useState('');
  const [macroAuthor, setMacroAuthor] = useState('');
  const [macroCategory, setMacroCategory] = useState('');
  const [macroTags, setMacroTags] = useState<string[]>([]);
  const [macroText, setMacroText] = useState('');
  const [macroActions, setMacroActions] = useState<MacroAction[]>([]);
  const [isPublic, setIsPublic] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [savedMacros, setSavedMacros] = useState<any[]>([]);
  const [selectedMacro, setSelectedMacro] = useState<string | null>(null);
  const [shareId, setShareId] = useState('');
  const [importText, setImportText] = useState('');
  const [syntaxTest, setSyntaxTest] = useState<any>(null);

  const categories = [
    'combat', 'crafting', 'movement', 'social', 'inventory', 'utility', 'custom'
  ];

  const actionTypes = [
    { value: 'command', label: 'Command', icon: '⚡' },
    { value: 'pause', label: 'Pause', icon: '⏸️' },
    { value: 'loop', label: 'Loop', icon: '🔄' },
    { value: 'condition', label: 'Condition', icon: '❓' },
    { value: 'variable', label: 'Variable', icon: '📝' },
    { value: 'comment', label: 'Comment', icon: '💬' }
  ];

  useEffect(() => {
    loadSavedMacros();
  }, []);

  const loadSavedMacros = async () => {
    try {
      setLoading(true);
      // Simulate API call to load saved macros
      const mockMacros = [
        {
          name: 'Combat Attack',
          description: 'Basic combat attack macro',
          category: 'combat',
          author: 'Player1',
          action_count: 5,
          created_date: '2024-12-19T10:30:00Z',
          tags: ['combat', 'attack']
        },
        {
          name: 'Resource Harvest',
          description: 'Harvest resources from survey',
          category: 'crafting',
          author: 'Player2',
          action_count: 8,
          created_date: '2024-12-18T15:20:00Z',
          tags: ['crafting', 'harvest']
        }
      ];
      setSavedMacros(mockMacros);
    } catch (err) {
      setError('Failed to load saved macros');
    } finally {
      setLoading(false);
    }
  };

  const addAction = () => {
    const newAction: MacroAction = {
      id: Date.now().toString(),
      type: 'command',
      command: '',
      parameters: {},
      delay_ms: 0,
      description: '',
      is_conditional: false
    };
    setMacroActions([...macroActions, newAction]);
  };

  const updateAction = (id: string, field: keyof MacroAction, value: any) => {
    setMacroActions(prev => prev.map(action => 
      action.id === id ? { ...action, [field]: value } : action
    ));
  };

  const removeAction = (id: string) => {
    setMacroActions(prev => prev.filter(action => action.id !== id));
  };

  const moveAction = (id: string, direction: 'up' | 'down') => {
    setMacroActions(prev => {
      const index = prev.findIndex(action => action.id === id);
      if (index === -1) return prev;
      
      const newActions = [...prev];
      if (direction === 'up' && index > 0) {
        [newActions[index], newActions[index - 1]] = [newActions[index - 1], newActions[index]];
      } else if (direction === 'down' && index < newActions.length - 1) {
        [newActions[index], newActions[index + 1]] = [newActions[index + 1], newActions[index]];
      }
      return newActions;
    });
  };

  const generateMacroText = () => {
    const lines: string[] = [];
    
    for (const action of macroActions) {
      switch (action.type) {
        case 'comment':
          lines.push(`# ${action.description}`);
          break;
        case 'pause':
          const duration = action.delay_ms >= 1000 ? `${action.delay_ms / 1000}s` : `${action.delay_ms}ms`;
          lines.push(`pause ${duration}`);
          break;
        case 'loop':
          const count = action.parameters.count || 1;
          const content = action.parameters.content || '';
          lines.push(`loop ${count} times: ${content}`);
          break;
        case 'condition':
          lines.push(`if ${action.condition}`);
          break;
        case 'variable':
          const varName = action.parameters.name || '';
          const varValue = action.parameters.value || '';
          lines.push(`var ${varName} = ${varValue}`);
          break;
        case 'command':
        default:
          const target = action.parameters.target || '';
          lines.push(`${action.command} ${target}`);
          break;
      }
    }
    
    return lines.join('\n');
  };

  const testMacroSyntax = async () => {
    try {
      setLoading(true);
      const macroText = generateMacroText();
      
      // Simulate API call for syntax testing
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockTestResult = {
        success: true,
        actions_parsed: macroActions.length,
        validation: {
          valid: true,
          errors: [],
          warnings: macroActions.length === 0 ? ['Macro has no actions'] : [],
          action_count: macroActions.length,
          estimated_duration: macroActions.reduce((sum, action) => sum + action.delay_ms, 0)
        },
        preview: macroText
      };
      
      setSyntaxTest(mockTestResult);
      setSuccess('Macro syntax test completed successfully');
      onMacroTest?.(macroText);
    } catch (err) {
      setError('Failed to test macro syntax');
    } finally {
      setLoading(false);
    }
  };

  const saveMacro = async () => {
    try {
      setLoading(true);
      
      if (!macroName.trim()) {
        setError('Macro name is required');
        return;
      }
      
      const macro: MacroDefinition = {
        name: macroName,
        description: macroDescription,
        author: macroAuthor,
        category: macroCategory,
        tags: macroTags,
        actions: macroActions,
        variables: {},
        settings: {},
        is_public: isPublic
      };
      
      // Simulate API call to save macro
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Macro saved successfully');
      onMacroSave?.(macro);
      
      // Reset form
      setMacroName('');
      setMacroDescription('');
      setMacroAuthor('');
      setMacroCategory('');
      setMacroTags([]);
      setMacroActions([]);
      setIsPublic(false);
      
    } catch (err) {
      setError('Failed to save macro');
    } finally {
      setLoading(false);
    }
  };

  const loadMacro = async (name: string) => {
    try {
      setLoading(true);
      
      // Simulate API call to load macro
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock macro data
      const mockMacro = {
        name: name,
        description: 'Loaded macro description',
        author: 'Original Author',
        category: 'combat',
        tags: ['loaded', 'macro'],
        actions: [
          {
            id: '1',
            type: 'command' as const,
            command: 'attack',
            parameters: { target: 'nearest enemy' },
            delay_ms: 0,
            description: 'Attack nearest enemy',
            is_conditional: false
          }
        ]
      };
      
      setMacroName(mockMacro.name);
      setMacroDescription(mockMacro.description);
      setMacroAuthor(mockMacro.author);
      setMacroCategory(mockMacro.category);
      setMacroTags(mockMacro.tags);
      setMacroActions(mockMacro.actions);
      
      setSuccess(`Loaded macro: ${name}`);
      onMacroLoad?.(name);
      
    } catch (err) {
      setError('Failed to load macro');
    } finally {
      setLoading(false);
    }
  };

  const shareMacro = async (name: string) => {
    try {
      setLoading(true);
      
      // Simulate API call to share macro
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockShareId = 'abc123def456';
      setShareId(mockShareId);
      setSuccess(`Macro shared! Share ID: ${mockShareId}`);
      
    } catch (err) {
      setError('Failed to share macro');
    } finally {
      setLoading(false);
    }
  };

  const importSharedMacro = async () => {
    try {
      setLoading(true);
      
      if (!shareId.trim()) {
        setError('Share ID is required');
        return;
      }
      
      // Simulate API call to import shared macro
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Shared macro imported successfully');
      setShareId('');
      
    } catch (err) {
      setError('Failed to import shared macro');
    } finally {
      setLoading(false);
    }
  };

  const importMacroCollection = async () => {
    try {
      setLoading(true);
      
      if (!importText.trim()) {
        setError('Import text is required');
        return;
      }
      
      // Simulate API call to import macro collection
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess('Macro collection imported successfully');
      setImportText('');
      
    } catch (err) {
      setError('Failed to import macro collection');
    } finally {
      setLoading(false);
    }
  };

  const addTag = (tag: string) => {
    if (tag.trim() && !macroTags.includes(tag.trim())) {
      setMacroTags([...macroTags, tag.trim()]);
    }
  };

  const removeTag = (tag: string) => {
    setMacroTags(macroTags.filter(t => t !== tag));
  };

  const renderBuilder = () => (
    <div className="macro-builder">
      <div className="builder-header">
        <h3>Create New Macro</h3>
        <p>Build your macro step by step or use the text editor</p>
      </div>

      <div className="builder-form">
        <div className="form-row">
          <div className="form-group">
            <label>Macro Name *</label>
            <input
              type="text"
              value={macroName}
              onChange={(e) => setMacroName(e.target.value)}
              placeholder="Enter macro name"
            />
          </div>
          <div className="form-group">
            <label>Category</label>
            <select
              value={macroCategory}
              onChange={(e) => setMacroCategory(e.target.value)}
            >
              <option value="">Select category</option>
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            value={macroDescription}
            onChange={(e) => setMacroDescription(e.target.value)}
            placeholder="Describe what this macro does"
            rows={3}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Author</label>
            <input
              type="text"
              value={macroAuthor}
              onChange={(e) => setMacroAuthor(e.target.value)}
              placeholder="Your name"
            />
          </div>
          <div className="form-group">
            <label>Tags</label>
            <div className="tags-input">
              <input
                type="text"
                placeholder="Add tag and press Enter"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addTag(e.currentTarget.value);
                    e.currentTarget.value = '';
                  }
                }}
              />
              <div className="tags-list">
                {macroTags.map(tag => (
                  <span key={tag} className="tag">
                    {tag}
                    <button onClick={() => removeTag(tag)}>×</button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={isPublic}
              onChange={(e) => setIsPublic(e.target.checked)}
            />
            Make this macro public (shareable)
          </label>
        </div>
      </div>

      <div className="actions-section">
        <div className="actions-header">
          <h4>Macro Actions</h4>
          <button className="btn btn-primary" onClick={addAction}>
            + Add Action
          </button>
        </div>

        <div className="actions-list">
          {macroActions.map((action, index) => (
            <div key={action.id} className="action-item">
              <div className="action-header">
                <span className="action-number">{index + 1}</span>
                <select
                  value={action.type}
                  onChange={(e) => updateAction(action.id, 'type', e.target.value)}
                >
                  {actionTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </option>
                  ))}
                </select>
                <div className="action-controls">
                  <button
                    className="btn btn-sm btn-outline"
                    onClick={() => moveAction(action.id, 'up')}
                    disabled={index === 0}
                  >
                    ↑
                  </button>
                  <button
                    className="btn btn-sm btn-outline"
                    onClick={() => moveAction(action.id, 'down')}
                    disabled={index === macroActions.length - 1}
                  >
                    ↓
                  </button>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => removeAction(action.id)}
                  >
                    ×
                  </button>
                </div>
              </div>

              <div className="action-content">
                {action.type === 'command' && (
                  <div className="form-row">
                    <div className="form-group">
                      <label>Command</label>
                      <input
                        type="text"
                        value={action.command}
                        onChange={(e) => updateAction(action.id, 'command', e.target.value)}
                        placeholder="e.g., attack, move, harvest"
                      />
                    </div>
                    <div className="form-group">
                      <label>Target/Parameters</label>
                      <input
                        type="text"
                        value={action.parameters.target || ''}
                        onChange={(e) => updateAction(action.id, 'parameters', { ...action.parameters, target: e.target.value })}
                        placeholder="e.g., nearest enemy, waypoint 1234"
                      />
                    </div>
                  </div>
                )}

                {action.type === 'pause' && (
                  <div className="form-group">
                    <label>Duration (ms)</label>
                    <input
                      type="number"
                      value={action.delay_ms}
                      onChange={(e) => updateAction(action.id, 'delay_ms', parseInt(e.target.value) || 0)}
                      min="0"
                      step="100"
                    />
                  </div>
                )}

                {action.type === 'loop' && (
                  <div className="form-row">
                    <div className="form-group">
                      <label>Loop Count</label>
                      <input
                        type="number"
                        value={action.parameters.count || 1}
                        onChange={(e) => updateAction(action.id, 'parameters', { ...action.parameters, count: parseInt(e.target.value) || 1 })}
                        min="1"
                        max="1000"
                      />
                    </div>
                    <div className="form-group">
                      <label>Loop Content</label>
                      <input
                        type="text"
                        value={action.parameters.content || ''}
                        onChange={(e) => updateAction(action.id, 'parameters', { ...action.parameters, content: e.target.value })}
                        placeholder="e.g., harvest resource"
                      />
                    </div>
                  </div>
                )}

                {action.type === 'condition' && (
                  <div className="form-group">
                    <label>Condition</label>
                    <input
                      type="text"
                      value={action.condition || ''}
                      onChange={(e) => updateAction(action.id, 'condition', e.target.value)}
                      placeholder="e.g., target exists, health > 50%"
                    />
                  </div>
                )}

                {action.type === 'variable' && (
                  <div className="form-row">
                    <div className="form-group">
                      <label>Variable Name</label>
                      <input
                        type="text"
                        value={action.parameters.name || ''}
                        onChange={(e) => updateAction(action.id, 'parameters', { ...action.parameters, name: e.target.value })}
                        placeholder="e.g., target"
                      />
                    </div>
                    <div className="form-group">
                      <label>Value</label>
                      <input
                        type="text"
                        value={action.parameters.value || ''}
                        onChange={(e) => updateAction(action.id, 'parameters', { ...action.parameters, value: e.target.value })}
                        placeholder="e.g., nearest enemy"
                      />
                    </div>
                  </div>
                )}

                {action.type === 'comment' && (
                  <div className="form-group">
                    <label>Comment</label>
                    <input
                      type="text"
                      value={action.description}
                      onChange={(e) => updateAction(action.id, 'description', e.target.value)}
                      placeholder="Add a comment"
                    />
                  </div>
                )}

                <div className="form-group">
                  <label>Description (optional)</label>
                  <input
                    type="text"
                    value={action.description}
                    onChange={(e) => updateAction(action.id, 'description', e.target.value)}
                    placeholder="Brief description of this action"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="builder-actions">
        <button className="btn btn-secondary" onClick={testMacroSyntax} disabled={loading}>
          {loading ? 'Testing...' : 'Test Syntax'}
        </button>
        <button className="btn btn-primary" onClick={saveMacro} disabled={loading || !macroName.trim()}>
          {loading ? 'Saving...' : 'Save Macro'}
        </button>
      </div>

      {syntaxTest && (
        <div className="syntax-test-results">
          <h4>Syntax Test Results</h4>
          <div className={`test-status ${syntaxTest.success ? 'success' : 'error'}`}>
            {syntaxTest.success ? '✅ Valid' : '❌ Invalid'}
          </div>
          <div className="test-details">
            <p>Actions parsed: {syntaxTest.actions_parsed}</p>
            <p>Estimated duration: {syntaxTest.validation.estimated_duration}ms</p>
            {syntaxTest.validation.errors.length > 0 && (
              <div className="test-errors">
                <strong>Errors:</strong>
                <ul>
                  {syntaxTest.validation.errors.map((error: string, index: number) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
            {syntaxTest.validation.warnings.length > 0 && (
              <div className="test-warnings">
                <strong>Warnings:</strong>
                <ul>
                  {syntaxTest.validation.warnings.map((warning: string, index: number) => (
                    <li key={index}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  const renderLibrary = () => (
    <div className="macro-library">
      <div className="library-header">
        <h3>Saved Macros</h3>
        <button className="btn btn-primary" onClick={loadSavedMacros}>
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading macros...</div>
      ) : (
        <div className="macros-grid">
          {savedMacros.map(macro => (
            <div key={macro.name} className="macro-card">
              <div className="macro-card-header">
                <h4>{macro.name}</h4>
                <span className="macro-category">{macro.category}</span>
              </div>
              <p className="macro-description">{macro.description}</p>
              <div className="macro-meta">
                <span>By: {macro.author}</span>
                <span>{macro.action_count} actions</span>
                <span>{new Date(macro.created_date).toLocaleDateString()}</span>
              </div>
              <div className="macro-tags">
                {macro.tags.map(tag => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
              <div className="macro-actions">
                <button
                  className="btn btn-sm btn-primary"
                  onClick={() => loadMacro(macro.name)}
                >
                  Load
                </button>
                <button
                  className="btn btn-sm btn-outline"
                  onClick={() => shareMacro(macro.name)}
                >
                  Share
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderImport = () => (
    <div className="macro-import">
      <div className="import-section">
        <h3>Import Shared Macro</h3>
        <p>Enter a share ID to import a shared macro</p>
        
        <div className="form-group">
          <label>Share ID</label>
          <input
            type="text"
            value={shareId}
            onChange={(e) => setShareId(e.target.value)}
            placeholder="Enter share ID"
          />
        </div>
        
        <button className="btn btn-primary" onClick={importSharedMacro} disabled={loading}>
          {loading ? 'Importing...' : 'Import Macro'}
        </button>
      </div>

      <div className="import-section">
        <h3>Import Macro Collection</h3>
        <p>Paste JSON data to import multiple macros</p>
        
        <div className="form-group">
          <label>JSON Data</label>
          <textarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder="Paste JSON macro collection data here"
            rows={10}
          />
        </div>
        
        <button className="btn btn-primary" onClick={importMacroCollection} disabled={loading}>
          {loading ? 'Importing...' : 'Import Collection'}
        </button>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="macro-settings">
      <h3>Macro Builder Settings</h3>
      
      <div className="settings-section">
        <h4>General Settings</h4>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Auto-save drafts
          </label>
        </div>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Show syntax hints
          </label>
        </div>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Validate on save
          </label>
        </div>
      </div>

      <div className="settings-section">
        <h4>Validation Settings</h4>
        <div className="setting-item">
          <label>Validation Level:</label>
          <select defaultValue="strict">
            <option value="basic">Basic</option>
            <option value="strict">Strict</option>
            <option value="complete">Complete</option>
          </select>
        </div>
        <div className="setting-item">
          <label>Max Actions:</label>
          <input type="number" defaultValue={100} min="1" max="1000" />
        </div>
        <div className="setting-item">
          <label>Max Pause Time (seconds):</label>
          <input type="number" defaultValue={300} min="1" max="3600" />
        </div>
      </div>

      <div className="settings-actions">
        <button className="btn btn-primary">Save Settings</button>
        <button className="btn btn-outline">Reset to Defaults</button>
      </div>
    </div>
  );

  return (
    <div className="macro-builder-container">
      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
          <button onClick={() => setSuccess(null)}>×</button>
        </div>
      )}

      <div className="builder-header">
        <h2>🔧 Macro Builder</h2>
        <p>Create, test, and manage your macros with a user-friendly interface</p>
      </div>

      <div className="builder-tabs">
        <button 
          className={`tab ${activeTab === 'builder' ? 'active' : ''}`}
          onClick={() => setActiveTab('builder')}
        >
          🏗️ Builder
        </button>
        <button 
          className={`tab ${activeTab === 'library' ? 'active' : ''}`}
          onClick={() => setActiveTab('library')}
        >
          📚 Library
        </button>
        <button 
          className={`tab ${activeTab === 'import' ? 'active' : ''}`}
          onClick={() => setActiveTab('import')}
        >
          📥 Import
        </button>
        <button 
          className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
      </div>

      <div className="builder-content">
        {activeTab === 'builder' && renderBuilder()}
        {activeTab === 'library' && renderLibrary()}
        {activeTab === 'import' && renderImport()}
        {activeTab === 'settings' && renderSettings()}
      </div>
    </div>
  );
};

export default MacroBuilder; 