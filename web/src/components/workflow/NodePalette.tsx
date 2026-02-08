'use client';

interface NodePaletteProps {
  onClose: () => void;
  onAddNode: (type: string, nodeType: string, label: string) => void;
  isAdvancedMode: boolean;
}

const simpleNodes = [
  {
    category: 'Start',
    items: [
      { type: 'trigger', nodeType: 'form_submit', label: 'Form Submitted', icon: '📝' },
      { type: 'trigger', nodeType: 'schedule', label: 'On a Schedule', icon: '⏰' },
      { type: 'trigger', nodeType: 'email_received', label: 'Email Received', icon: '📧' },
      { type: 'trigger', nodeType: 'manual_trigger', label: 'Manual Start', icon: '👆' },
    ],
  },
  {
    category: 'Actions',
    items: [
      { type: 'action', nodeType: 'send_email', label: 'Send Email', icon: '✉️' },
      { type: 'action', nodeType: 'send_sms', label: 'Send SMS', icon: '📱' },
      { type: 'action', nodeType: 'update_spreadsheet', label: 'Update Spreadsheet', icon: '📊' },
      { type: 'action', nodeType: 'create_task', label: 'Create Task', icon: '✅' },
      { type: 'action', nodeType: 'send_notification', label: 'Send Notification', icon: '🔔' },
      { type: 'action', nodeType: 'wait', label: 'Wait', icon: '⏳' },
    ],
  },
  {
    category: 'Logic',
    items: [
      { type: 'condition', nodeType: 'if_else', label: 'If/Else', icon: '🔀' },
      { type: 'approval', nodeType: 'approval', label: 'Wait for Approval', icon: '✋' },
    ],
  },
];

const advancedNodes = [
  ...simpleNodes,
  {
    category: 'Advanced',
    items: [
      { type: 'trigger', nodeType: 'webhook', label: 'Webhook', icon: '🔗' },
      { type: 'action', nodeType: 'http_request', label: 'HTTP Request', icon: '🌐' },
      { type: 'action', nodeType: 'javascript', label: 'Run Code', icon: '💻' },
      { type: 'action', nodeType: 'filter', label: 'Filter', icon: '🔍' },
      { type: 'action', nodeType: 'transform', label: 'Transform Data', icon: '🔄' },
    ],
  },
];

export default function NodePalette({
  onClose,
  onAddNode,
  isAdvancedMode,
}: NodePaletteProps) {
  const nodes = isAdvancedMode ? advancedNodes : simpleNodes;

  return (
    <div className="absolute top-16 left-4 w-72 bg-white rounded-xl border border-gray-200 shadow-xl z-10 max-h-[70vh] overflow-y-auto">
      <div className="sticky top-0 bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between">
        <h3 className="font-semibold">Add a Step</h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      </div>
      <div className="p-3">
        {nodes.map((category) => (
          <div key={category.category} className="mb-4">
            <div className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2 px-2">
              {category.category}
            </div>
            <div className="space-y-1">
              {category.items.map((item) => (
                <button
                  key={item.nodeType}
                  onClick={() => onAddNode(item.type, item.nodeType, item.label)}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 text-left transition"
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="text-sm">{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
