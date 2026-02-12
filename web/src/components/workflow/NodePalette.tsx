'use client';

import ServiceIcon from '@/components/ui/ServiceIcon';

interface NodePaletteProps {
  onClose: () => void;
  onAddNode: (type: string, nodeType: string, label: string) => void;
  isAdvancedMode: boolean;
}

const simpleNodes = [
  {
    category: 'Start',
    items: [
      { type: 'trigger', nodeType: 'start_form', label: 'Form Submitted' },
      { type: 'trigger', nodeType: 'start_schedule', label: 'On a Schedule' },
      { type: 'trigger', nodeType: 'start_email', label: 'Email Received' },
      { type: 'trigger', nodeType: 'start_manual', label: 'Manual Start' },
    ],
  },
  {
    category: 'Actions',
    items: [
      { type: 'action', nodeType: 'send_email', label: 'Send Email' },
      { type: 'action', nodeType: 'ai_reply', label: 'AI Reply' },
      { type: 'action', nodeType: 'ai_summarize', label: 'AI Summarize' },
      { type: 'action', nodeType: 'append_row', label: 'Add to Spreadsheet' },
      { type: 'action', nodeType: 'send_slack', label: 'Send Slack' },
      { type: 'action', nodeType: 'send_notification', label: 'Send Notification' },
      { type: 'action', nodeType: 'delay', label: 'Wait / Delay' },
    ],
  },
  {
    category: 'Payments (Stripe)',
    items: [
      { type: 'action', nodeType: 'stripe_create_invoice', label: 'Create Invoice' },
      { type: 'action', nodeType: 'stripe_send_invoice', label: 'Send Invoice' },
      { type: 'action', nodeType: 'stripe_create_payment_link', label: 'Payment Link' },
      { type: 'action', nodeType: 'stripe_get_customer', label: 'Get/Create Customer' },
    ],
  },
  {
    category: 'Logic',
    items: [
      { type: 'condition', nodeType: 'condition', label: 'If/Else' },
      { type: 'approval', nodeType: 'approval', label: 'Wait for Approval' },
    ],
  },
];

const advancedNodes = [
  ...simpleNodes,
  {
    category: 'Advanced',
    items: [
      { type: 'trigger', nodeType: 'start_webhook', label: 'Webhook' },
      { type: 'action', nodeType: 'http_request', label: 'HTTP Request' },
      { type: 'action', nodeType: 'read_sheet', label: 'Read Spreadsheet' },
      { type: 'action', nodeType: 'transform', label: 'Transform Data' },
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
                  <ServiceIcon type={item.nodeType} size={20} />
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
