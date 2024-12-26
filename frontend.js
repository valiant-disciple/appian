import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Eye, Code, Check, X, Columns, RefreshCw, AlertCircle } from 'lucide-react';

export default function HTMLModernizer() {
  const [html, setHtml] = useState('');
  const [improvements, setImprovements] = useState(null);
  const [selectedImprovements, setSelectedImprovements] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentPreview, setCurrentPreview] = useState('original');
  const [activeTab, setActiveTab] = useState('editor');
  const [previewMode, setPreviewMode] = useState('split');
  const [improvedHtml, setImprovedHtml] = useState('');
  const [hoveredImprovement, setHoveredImprovement] = useState(null);

  const analyzeHtml = async () => {
    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ html })
      });
      const data = await response.json();
      setImprovements(data.improvements);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const applyImprovements = async () => {
    try {
      const response = await fetch('/api/apply-improvements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          html,
          improvements: Object.values(selectedImprovements)
        })
      });
      const data = await response.json();
      setImprovedHtml(data.improved_html);
    } catch (error) {
      console.error('Failed to apply improvements:', error);
    }
  };

  useEffect(() => {
    if (Object.keys(selectedImprovements).length > 0) {
      applyImprovements();
    }
  }, [selectedImprovements]);

  const ImprovementCard = ({ improvement }) => (
    <div 
      className="border rounded p-4 hover:bg-gray-50 relative"
      onMouseEnter={() => setHoveredImprovement(improvement.id)}
      onMouseLeave={() => setHoveredImprovement(null)}
    >
      <div className="flex items-start space-x-3">
        <button
          className={`p-2 rounded ${
            selectedImprovements[improvement.id] ? 'bg-green-100 text-green-600' : 'bg-gray-100'
          }`}
          onClick={() => toggleImprovement(improvement.id)}
        >
          {selectedImprovements[improvement.id] ? <Check size={16} /> : <X size={16} />}
        </button>
        <div className="flex-1">
          <h3 className="font-medium">{improvement.suggestion}</h3>
          <p className="text-sm text-gray-600 mt-1">{improvement.explanation}</p>
          
          <div className="mt-2 space-y-2">
            <div className="text-xs bg-gray-50 p-2 rounded">
              <div className="font-medium">Original:</div>
              <code className="block mt-1">{improvement.original_code}</code>
            </div>
            <div className="text-xs bg-gray-50 p-2 rounded">
              <div className="font-medium">Improved:</div>
              <code className="block mt-1">{improvement.improved_code}</code>
            </div>
          </div>

          <div className="mt-2 flex items-center space-x-2">
            <span className={`text-xs px-2 py-1 rounded-full ${
              improvement.priority === 'high' ? 'bg-red-100 text-red-600' :
              improvement.priority === 'medium' ? 'bg-yellow-100 text-yellow-600' :
              'bg-blue-100 text-blue-600'
            }`}>
              {improvement.priority}
            </span>
            <span className="text-xs text-gray-500">
              {improvement.category}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-4">
      {/* ... Previous UI code ... */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-4">
          <textarea
            className="w-full h-96 p-4 font-mono text-sm border rounded"
            value={html}
            onChange={(e) => setHtml(e.target.value)}
            placeholder="Paste your HTML here..."
          />
          <button
            className="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300"
            onClick={analyzeHtml}
            disabled={!html || isAnalyzing}
          >
            {isAnalyzing ? 
              <><RefreshCw className="inline-block mr-2 animate-spin" size={16} />Analyzing...</> : 
              'Analyze with AI'
            }
          </button>
        </div>

        <div className="border rounded">
          <div className="p-4 bg-gray-50 border-b">
            <h2 className="font-medium">AI Suggested Improvements</h2>
          </div>
          <div className="p-4 space-y-4 overflow-y-auto h-96">
            {improvements ? (
              improvements.map(improvement => (
                <ImprovementCard 
                  key={improvement.id} 
                  improvement={improvement}
                />
              ))
            ) : (
              <div className="text-center text-gray-500">
                No improvements suggested yet. Paste your HTML and click Analyze.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preview Panel */}
      {activeTab === 'preview' && (
        <div className={`grid ${previewMode === 'split' ? 'grid-cols-2' : 'grid-cols-1'} gap-4 h-96 mt-4`}>
          {(previewMode === 'split' || currentPreview === 'original') && (
            <div className="border rounded overflow-hidden">
              <div className="bg-gray-50 p-2 border-b">Original</div>
              <iframe
                srcDoc={html}
                className="w-full h-full"
                title="Original"
              />
            </div>
          )}
          {(previewMode === 'split' || currentPreview === 'improved') && (
            <div className="border rounded overflow-hidden">
              <div className="bg-gray-50 p-2 border-b">
                Improved ({Object.keys(selectedImprovements).length} changes)
              </div>
              <iframe
                srcDoc={improvedHtml || html}
                className="w-full h-full"
                title="Improved"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}