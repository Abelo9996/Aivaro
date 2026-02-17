'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Connection,
  Edge,
  Node,
  Panel,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { api } from '@/lib/api';
import { useModeStore } from '@/stores/modeStore';
import NodePalette from '@/components/workflow/NodePalette';
import NodeInspector from '@/components/workflow/NodeInspector';
import TriggerNode from '@/components/workflow/nodes/TriggerNode';
import ActionNode from '@/components/workflow/nodes/ActionNode';
import ConditionNode from '@/components/workflow/nodes/ConditionNode';
import ApprovalNode from '@/components/workflow/nodes/ApprovalNode';
import ExecutionProgress from '@/components/workflow/ExecutionProgress';
import type { Workflow, WorkflowNode } from '@/types';

const nodeTypes = {
  trigger: TriggerNode,
  action: ActionNode,
  condition: ConditionNode,
  approval: ApprovalNode,
};

// Step type for execution progress
interface ExecutionStep {
  node_id: string;
  node_label: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type FlowNode = Node<any>;

export default function WorkflowEditorPage() {
  const params = useParams();
  const router = useRouter();
  const { isAdvancedMode } = useModeStore();
  
  const [nodes, setNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [showPalette, setShowPalette] = useState(false);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [isActive, setIsActive] = useState(false);
  const [activating, setActivating] = useState(false);
  
  // Execution progress state
  const [showProgress, setShowProgress] = useState(false);
  const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
  const [executionStatus, setExecutionStatus] = useState<'running' | 'completed' | 'failed'>('running');
  const [completedSteps, setCompletedSteps] = useState(0);
  const [currentStep, setCurrentStep] = useState<string | undefined>();
  const [executionId, setExecutionId] = useState<string | undefined>();

  const workflowId = params.id as string;
  const isNew = workflowId === 'new';

  // Helper function to map node types to React Flow node categories
  const getNodeCategory = (nodeType: string): string => {
    // Trigger/Start nodes
    if (nodeType.startsWith('start_') || nodeType.includes('trigger') || nodeType === 'webhook') {
      return 'trigger';
    }
    // Condition nodes
    if (nodeType === 'condition' || nodeType === 'filter' || nodeType === 'branch') {
      return 'condition';
    }
    // Approval nodes
    if (nodeType === 'approval' || nodeType === 'human_review') {
      return 'approval';
    }
    // Everything else is an action
    return 'action';
  };

  useEffect(() => {
    const loadData = async () => {
      setError(null);
      
      if (isNew) {
        // Create a new workflow with default trigger
        const defaultNodes: Node[] = [
          {
            id: 'trigger-1',
            type: 'trigger',
            position: { x: 250, y: 100 },
            data: { 
              label: 'When this happens...',
              nodeType: 'manual_trigger',
              config: {},
            },
          },
        ];
        setNodes(defaultNodes);
        setEdges([]);
        setLoading(false);
      } else {
        try {
          const workflow = await api.getWorkflow(workflowId);
          
          if (!workflow) {
            setError('Workflow not found');
            setLoading(false);
            return;
          }
          
          setWorkflowName(workflow.name || 'Untitled Workflow');
          setIsActive(workflow.is_active || false);
          
          // Helper function to map node types
          const mapNodeType = (nodeType: string): string => {
            if (nodeType.startsWith('start_') || nodeType.includes('trigger') || nodeType === 'webhook') {
              return 'trigger';
            }
            if (nodeType === 'condition' || nodeType === 'filter' || nodeType === 'branch') {
              return 'condition';
            }
            if (nodeType === 'approval' || nodeType === 'human_review') {
              return 'approval';
            }
            return 'action';
          };
          
          // Convert workflow nodes to React Flow nodes
          const flowNodes: Node[] = (workflow.nodes || []).map((node: WorkflowNode, index: number) => ({
            id: node.id,
            type: mapNodeType(node.type),
            position: node.position || { x: 250, y: 100 + index * 150 },
            data: {
              label: node.label || node.type,
              nodeType: node.type,
              config: node.config || node.parameters || {},
              requiresApproval: node.requiresApproval || false,
            },
          }));
          
          // Convert workflow edges
          const flowEdges: Edge[] = (workflow.edges || []).map((edge: any) => ({
            id: edge.id || `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
            sourceHandle: edge.sourceHandle,
            targetHandle: edge.targetHandle,
            animated: true,
            style: { stroke: '#6366f1' },
          }));
          
          setNodes(flowNodes);
          setEdges(flowEdges);
        } catch (err: any) {
          console.error('Failed to load workflow:', err);
          setError(err.message || 'Failed to load workflow');
        } finally {
          setLoading(false);
        }
      }
    };
    
    loadData();
  }, [workflowId, isNew, setNodes, setEdges]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds));
    },
    [setEdges]
  );

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  const handleAddNode = (type: string, nodeType: string, label: string) => {
    const newNode: Node = {
      id: `${type}-${Date.now()}`,
      type,
      position: { x: 250, y: (nodes.length + 1) * 150 },
      data: {
        label,
        nodeType,
        config: {},
      },
    };
    setNodes((nds) => [...nds, newNode]);
    setShowPalette(false);
  };

  const handleUpdateNode = (nodeId: string, data: any) => {
    setNodes((nds) =>
      nds.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
      )
    );
  };

  const handleDeleteNode = (nodeId: string) => {
    setNodes((nds) => nds.filter((n) => n.id !== nodeId));
    setEdges((eds) => eds.filter((e) => e.source !== nodeId && e.target !== nodeId));
    setSelectedNode(null);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const workflowData = {
        name: workflowName,
        nodes: nodes.map((n) => ({
          id: n.id,
          type: n.data.nodeType,
          label: n.data.label,
          position: n.position,
          parameters: n.data.config || {},
          requiresApproval: n.data.requiresApproval || false,
        })),
        edges: edges.map((e) => ({
          id: e.id,
          source: e.source,
          target: e.target,
          sourceHandle: e.sourceHandle,
          targetHandle: e.targetHandle,
        })),
      };

      if (isNew) {
        const created = await api.createWorkflow(workflowData);
        router.push(`/app/workflows/${created.id}`);
      } else {
        await api.updateWorkflow(workflowId, workflowData);
      }
    } catch (err) {
      console.error('Failed to save workflow:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async () => {
    if (isNew) return;
    
    setActivating(true);
    try {
      await api.updateWorkflow(workflowId, { is_active: !isActive });
      setIsActive(!isActive);
    } catch (err) {
      console.error('Failed to toggle workflow status:', err);
    } finally {
      setActivating(false);
    }
  };

  const handleTestRun = async () => {
    // Initialize progress UI
    setShowProgress(true);
    setExecutionStatus('running');
    setCompletedSteps(0);
    setCurrentStep(undefined);
    setExecutionId(undefined);
    
    // Build initial steps from workflow nodes
    const initialSteps: ExecutionStep[] = nodes.map(n => ({
      node_id: n.id,
      node_label: n.data.label || n.data.nodeType || 'Step',
      status: 'pending' as const,
    }));
    setExecutionSteps(initialSteps);
    
    try {
      const { promise } = api.runWorkflowWithProgress(
        workflowId,
        true, // isTest = true
        undefined,
        (data) => {
          if (data.type === 'start') {
            setExecutionId(data.execution_id);
          } else if (data.type === 'step') {
            setCompletedSteps(data.completed || 0);
            setCurrentStep(data.node_label);
            
            // Update step status
            setExecutionSteps(prev => prev.map(step => 
              step.node_id === data.node_id 
                ? { ...step, status: data.status as 'completed' | 'failed' }
                : step
            ));
          } else if (data.type === 'complete') {
            setExecutionStatus(data.status === 'completed' ? 'completed' : 'failed');
            setExecutionId(data.execution_id);
          }
        }
      );
      
      await promise;
    } catch (err) {
      console.error('Failed to run test:', err);
      setExecutionStatus('failed');
    }
  };

  const handleRealRun = async () => {
    if (!confirm('This will run the workflow for real. Emails will be sent, sheets will be modified, etc. Continue?')) {
      return;
    }
    
    // Initialize progress UI
    setShowProgress(true);
    setExecutionStatus('running');
    setCompletedSteps(0);
    setCurrentStep(undefined);
    setExecutionId(undefined);
    
    // Build initial steps from workflow nodes
    const initialSteps: ExecutionStep[] = nodes.map(n => ({
      node_id: n.id,
      node_label: n.data.label || n.data.nodeType || 'Step',
      status: 'pending' as const,
    }));
    setExecutionSteps(initialSteps);
    
    try {
      const { promise } = api.runWorkflowWithProgress(
        workflowId,
        false, // isTest = false - REAL RUN
        undefined,
        (data) => {
          if (data.type === 'start') {
            setExecutionId(data.execution_id);
          } else if (data.type === 'step') {
            setCompletedSteps(data.completed || 0);
            setCurrentStep(data.node_label);
            
            // Update step status
            setExecutionSteps(prev => prev.map(step => 
              step.node_id === data.node_id 
                ? { ...step, status: data.status as 'completed' | 'failed' }
                : step
            ));
          } else if (data.type === 'complete') {
            setExecutionStatus(data.status === 'completed' ? 'completed' : 'failed');
            setExecutionId(data.execution_id);
          }
        }
      );
      
      await promise;
    } catch (err) {
      console.error('Failed to run workflow:', err);
      setExecutionStatus('failed');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading workflow...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/app/workflows')}
            className="text-gray-500 hover:text-gray-700"
          >
            ←
          </button>
          <input
            type="text"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="text-lg font-semibold bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-2"
          />
        </div>
        <div className="flex items-center gap-3">
          {!isNew && (
            <>
              <button
                onClick={handleToggleActive}
                disabled={activating}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {activating ? '...' : isActive ? '✓ Active' : '○ Inactive'}
              </button>
              <button
                onClick={handleTestRun}
                className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                🧪 Test
              </button>
              <button
                onClick={handleRealRun}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700"
              >
                ▶ Run Now
              </button>
            </>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Canvas */}
      <div className="flex-1 flex">
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onPaneClick={onPaneClick}
            nodeTypes={nodeTypes}
            fitView
            className="bg-gray-50"
          >
            <Background />
            <Controls />
            <MiniMap />
            <Panel position="top-left">
              <button
                onClick={() => setShowPalette(!showPalette)}
                className="bg-white border border-gray-200 shadow-sm px-4 py-2 rounded-lg font-medium hover:bg-gray-50"
              >
                + Add Step
              </button>
            </Panel>
          </ReactFlow>

          {/* Node Palette */}
          {showPalette && (
            <NodePalette
              onClose={() => setShowPalette(false)}
              onAddNode={handleAddNode}
              isAdvancedMode={isAdvancedMode}
            />
          )}
        </div>

        {/* Node Inspector */}
        {selectedNode && (
          <NodeInspector
            node={selectedNode}
            onUpdate={handleUpdateNode}
            onDelete={handleDeleteNode}
            onClose={() => setSelectedNode(null)}
            isAdvancedMode={isAdvancedMode}
            workflowId={params.id as string}
          />
        )}
      </div>

      {/* Execution Progress Modal */}
      <ExecutionProgress
        isOpen={showProgress}
        workflowName={workflowName}
        totalSteps={executionSteps.length}
        completedSteps={completedSteps}
        currentStep={currentStep}
        steps={executionSteps}
        status={executionStatus}
        executionId={executionId}
        onClose={() => setShowProgress(false)}
        onViewExecution={() => {
          setShowProgress(false);
          if (executionId) {
            router.push(`/app/executions/${executionId}`);
          }
        }}
      />
    </div>
  );
}
