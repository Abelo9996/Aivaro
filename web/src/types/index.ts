export interface User {
  id: string;
  email: string;
  full_name?: string;
  business_type?: string;
  onboarding_completed: boolean;
  email_verified?: boolean;
  plan?: string;
  created_at: string;
}

export interface WorkflowNode {
  id: string;
  type: string;
  label: string;
  position: { x: number; y: number };
  parameters?: Record<string, any>;
  config?: Record<string, any>;
  connectionId?: string;
  requiresApproval?: boolean;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
}

export interface Workflow {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  summary?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExecutionNode {
  id: string;
  node_id: string;
  node_type: string;
  node_label?: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'waiting_approval' | 'skipped';
  input?: Record<string, any>;
  output?: Record<string, any>;
  error?: string;
  logs?: string;
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
}

export interface Execution {
  id: string;
  workflow_id: string;
  status: 'running' | 'paused' | 'completed' | 'failed' | 'pending_approval';
  error?: string;
  is_test: boolean;
  started_at: string;
  completed_at?: string;
  current_node_id?: string;
  trigger_data?: Record<string, any>;
  node_executions?: ExecutionNode[];
}

export interface Approval {
  id: string;
  execution_id: string;
  node_id: string;
  node_type: string;
  status: 'pending' | 'approved' | 'rejected';
  message?: string;
  action_summary?: string;
  action_data?: Record<string, any>;
  action_details?: Record<string, any>;
  workflow_name?: string;
  step_label?: string;
  approved_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface Connection {
  id: string;
  user_id: string;
  name: string;
  type: string;
  is_connected: boolean;
  created_at: string;
  updated_at: string;
}

export interface Template {
  id: string;
  name: string;
  description?: string;
  summary?: string;
  icon?: string;
  category: string;
  business_types?: string[];
  definition: {
    nodes?: WorkflowNode[];
    edges?: WorkflowEdge[];
  };
  created_at: string;
}

export type NodeType = 
  | 'start_manual'
  | 'start_form'
  | 'send_email'
  | 'append_row'
  | 'delay'
  | 'send_notification';

export interface NodeTypeConfig {
  type: NodeType;
  label: string;
  friendlyName: string;
  description: string;
  icon: string;
  color: string;
  defaultParameters: Record<string, any>;
  requiresApproval: boolean;
  isAdvanced: boolean;
}

export const NODE_TYPES: Record<NodeType, NodeTypeConfig> = {
  start_manual: {
    type: 'start_manual',
    label: 'Start',
    friendlyName: 'When you run this',
    description: 'Manually start the workflow',
    icon: 'Play',
    color: 'bg-green-500',
    defaultParameters: {},
    requiresApproval: false,
    isAdvanced: false,
  },
  start_form: {
    type: 'start_form',
    label: 'Start',
    friendlyName: 'When a form is submitted',
    description: 'Start when someone fills out a form',
    icon: 'FileText',
    color: 'bg-green-500',
    defaultParameters: {},
    requiresApproval: false,
    isAdvanced: false,
  },
  send_email: {
    type: 'send_email',
    label: 'Send Email',
    friendlyName: 'Send an email',
    description: 'Send an email to someone',
    icon: 'Mail',
    color: 'bg-blue-500',
    defaultParameters: { to: '', subject: '', body: '' },
    requiresApproval: true,
    isAdvanced: false,
  },
  append_row: {
    type: 'append_row',
    label: 'Add to Spreadsheet',
    friendlyName: 'Add a row to spreadsheet',
    description: 'Add data to your spreadsheet',
    icon: 'Table',
    color: 'bg-emerald-500',
    defaultParameters: { spreadsheet: '', columns: [] },
    requiresApproval: false,
    isAdvanced: false,
  },
  delay: {
    type: 'delay',
    label: 'Wait',
    friendlyName: 'Wait for some time',
    description: 'Pause the workflow for a duration',
    icon: 'Clock',
    color: 'bg-amber-500',
    defaultParameters: { duration: 24, unit: 'hours' },
    requiresApproval: false,
    isAdvanced: false,
  },
  send_notification: {
    type: 'send_notification',
    label: 'Notify',
    friendlyName: 'Send you a notification',
    description: 'Get notified about something',
    icon: 'Bell',
    color: 'bg-purple-500',
    defaultParameters: { message: '' },
    requiresApproval: false,
    isAdvanced: false,
  },
};
