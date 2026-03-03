'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
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
import dagre from 'dagre';
import { api } from '@/lib/api';
import { useModeStore } from '@/stores/modeStore';
import NodePalette from '@/components/workflow/NodePalette';
import NodeInspector from '@/components/workflow/NodeInspector';
import TriggerNode from '@/components/workflow/nodes/TriggerNode';
import ActionNode from '@/components/workflow/nodes/ActionNode';
import ConditionNode from '@/components/workflow/nodes/ConditionNode';
import ApprovalNode from '@/components/workflow/nodes/ApprovalNode';
import ExecutionProgress from '@/components/workflow/ExecutionProgress';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import type { Workflow, WorkflowNode } from '@/types';

const nodeTypes = {
  trigger: TriggerNode,
  action: ActionNode,
  condition: ConditionNode,
  approval: ApprovalNode,
};

interface ExecutionStep {
  node_id: string;
  node_label: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type FlowNode = Node<any>;

// Auto-layout using dagre
function autoLayout(nodes: FlowNode[], edges: Edge[]): FlowNode[] {
  if (nodes.length === 0) return nodes;
  
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'TB', nodesep: 80, ranksep: 120, marginx: 50, marginy: 50 });
  
  nodes.forEach((node) => {
    g.setNode(node.id, { width: 240, height: 80 });
  });
  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });
  
  dagre.layout(g);
  
  return nodes.map((node) => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: { x: pos.x - 120, y: pos.y - 40 },
    };
  });
}

const getNodeCategory = (nodeType: string): string => {
  if (nodeType.startsWith('start_') || nodeType.includes('trigger') || nodeType === 'webhook') return 'trigger';
  if (nodeType === 'condition' || nodeType === 'filter' || nodeType === 'branch') return 'condition';
  if (nodeType === 'approval' || nodeType === 'human_review') return 'approval';
  return 'action';
};

export default function WorkflowEditorPage() {
  const params = useParams();
  const router = useRouter();
  const { isAdvancedMode } = useModeStore();
  
  const [nodes, setNodes, onNodesChange] = useNodesState<FlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showPalette, setShowPalette] = useState(false);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [isActive, setIsActive] = useState(false);
  const [activating, setActivating] = useState(false);
  
  const [showProgress, setShowProgress] = useState(false);
  const [executionSteps, setExecutionSteps] = useState<ExecutionStep[]>([]);
  const [executionStatus, setExecutionStatus] = useState<'running' | 'completed' | 'failed'>('running');
  const [completedSteps, setCompletedSteps] = useState(0);
  const [currentStep, setCurrentStep] = useState<string | undefined>();
  const [executionId, setExecutionId] = useState<string | undefined>();
  const [showRunConfirm, setShowRunConfirm] = useState(false);

  const workflowId = params.id as string;
  const isNew = workflowId === 'new';

  // Derive selectedNode from current nodes state so it's always fresh
  const selectedNode = useMemo(
    () => (selectedNodeId ? nodes.find((n) => n.id === selectedNodeId) || null : null),
    [selectedNodeId, nodes]
  );

  useEffect(() => {
    const loadData = async () => {
      setError(null);
      
      if (isNew) {
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
          
          const flowNodes: Node[] = (workflow.nodes || []).map((node: WorkflowNode, index: number) => ({
            id: node.id,
            type: getNodeCategory(node.type),
            position: node.position || { x: 250, y: 100 + index * 150 },
            data: {
              label: node.label || node.type,
              nodeType: node.type,
              config: node.config || node.parameters || {},
              requiresApproval: node.requiresApproval || false,
            },
          }));
          
          const flowEdges: Edge[] = (workflow.edges || []).map((edge: any) => ({
            id: edge.id || `${edge.source}-${edge.target}`,
            source: edge.source,
            target: edge.target,
            sourceHandle: edge.sourceHandle,
            targetHandle: edge.targetHandle,
            label: edge.label || (edge.sourceHandle === 'yes' ? 'Yes' : edge.sourceHandle === 'no' ? 'No' : undefined),
            animated: true,
            style: { stroke: '#6366f1' },
            labelStyle: { fontSize: 12, fontWeight: 600 },
            labelBgStyle: { fill: '#f3f4f6', fillOpacity: 0.9 },
          }));
          
          // Auto-layout nodes for clean visualization
          const layoutNodes = autoLayout(flowNodes, flowEdges);
          
          setNodes(layoutNodes);
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
      setEdges((eds) => addEdge({ ...connection, animated: true, style: { stroke: '#6366f1' } }, eds));
    },
    [setEdges]
  );

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNodeId(node.id);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNodeId(null);
  }, []);

  // Issue 5: Handle edge click to select/delete
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

  const onEdgeClick = useCallback((_: React.MouseEvent, edge: Edge) => {
    setSelectedEdgeId(edge.id);
  }, []);

  const handleDeleteEdge = useCallback(() => {
    if (selectedEdgeId) {
      setEdges((eds) => eds.filter((e) => e.id !== selectedEdgeId));
      setSelectedEdgeId(null);
    }
  }, [selectedEdgeId, setEdges]);

  // Keyboard shortcut for deleting edges
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedEdgeId && !selectedNodeId) {
        handleDeleteEdge();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedEdgeId, selectedNodeId, handleDeleteEdge]);

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
    setSelectedNodeId(null);
  };

  // Issue 6: Auto-layout button
  const handleAutoLayout = () => {
    const layoutNodes = autoLayout(nodes, edges);
    setNodes(layoutNodes);
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
          label: e.label,
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
    setShowProgress(true);
    setExecutionStatus('running');
    setCompletedSteps(0);
    setCurrentStep(undefined);
    setExecutionId(undefined);
    
    const initialSteps: ExecutionStep[] = nodes.map(n => ({
      node_id: n.id,
      node_label: n.data.label || n.data.nodeType || 'Step',
      status: 'pending' as const,
    }));
    setExecutionSteps(initialSteps);
    
    try {
      const { promise } = api.runWorkflowWithProgress(
        workflowId, true, undefined,
        (data) => {
          if (data.type === 'start') setExecutionId(data.execution_id);
          else if (data.type === 'step') {
            setCompletedSteps(data.completed || 0);
            setCurrentStep(data.node_label);
            setExecutionSteps(prev => prev.map(step => 
              step.node_id === data.node_id ? { ...step, status: data.status as 'completed' | 'failed' } : step
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
    setShowRunConfirm(false);
    setShowProgress(true);
    setExecutionStatus('running');
    setCompletedSteps(0);
    setCurrentStep(undefined);
    setExecutionId(undefined);
    
    const initialSteps: ExecutionStep[] = nodes.map(n => ({
      node_id: n.id,
      node_label: n.data.label || n.data.nodeType || 'Step',
      status: 'pending' as const,
    }));
    setExecutionSteps(initialSteps);
    
    try {
      const { promise } = api.runWorkflowWithProgress(
        workflowId, false, undefined,
        (data) => {
          if (data.type === 'start') setExecutionId(data.execution_id);
          else if (data.type === 'step') {
            setCompletedSteps(data.completed || 0);
            setCurrentStep(data.node_label);
            setExecutionSteps(prev => prev.map(step => 
              step.node_id === data.node_id ? { ...step, status: data.status as 'completed' | 'failed' } : step
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

  // Highlight selected edge
  const styledEdges = useMemo(() => 
    edges.map((e) => ({
      ...e,
      style: {
        ...e.style,
        stroke: e.id === selectedEdgeId ? '#ef4444' : '#6366f1',
        strokeWidth: e.id === selectedEdgeId ? 3 : 2,
      },
    })),
    [edges, selectedEdgeId]
  );

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
          <button onClick={() => router.push('/app/workflows')} className="text-gray-500 hover:text-gray-700">
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
                  isActive ? 'bg-green-100 text-green-700 hover:bg-green-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {activating ? '...' : isActive ? '✓ Active' : '○ Inactive'}
              </button>
              <button onClick={handleTestRun} className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">
                🧪 Test
              </button>
              <button onClick={() => setShowRunConfirm(true)} className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700">
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
            edges={styledEdges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={() => { onPaneClick(); setSelectedEdgeId(null); }}
            nodeTypes={nodeTypes}
            deleteKeyCode="Delete"
            fitView
            className="bg-gray-50"
          >
            <Background />
            <Controls />
            <MiniMap />
            <Panel position="top-left">
              <div className="flex gap-2">
                <button
                  onClick={() => setShowPalette(!showPalette)}
                  className="bg-white border border-gray-200 shadow-sm px-4 py-2 rounded-lg font-medium hover:bg-gray-50"
                >
                  + Add Step
                </button>
                <button
                  onClick={handleAutoLayout}
                  className="bg-white border border-gray-200 shadow-sm px-4 py-2 rounded-lg font-medium hover:bg-gray-50"
                  title="Auto-arrange nodes"
                >
                  🔀 Auto Layout
                </button>
                {selectedEdgeId && (
                  <button
                    onClick={handleDeleteEdge}
                    className="bg-red-50 border border-red-200 shadow-sm px-4 py-2 rounded-lg font-medium text-red-600 hover:bg-red-100"
                  >
                    🗑 Delete Edge
                  </button>
                )}
              </div>
            </Panel>
          </ReactFlow>

          {showPalette && (
            <NodePalette
              onClose={() => setShowPalette(false)}
              onAddNode={handleAddNode}
              isAdvancedMode={isAdvancedMode}
            />
          )}
        </div>

        {selectedNode && (
          <NodeInspector
            node={selectedNode}
            onUpdate={handleUpdateNode}
            onDelete={handleDeleteNode}
            onClose={() => setSelectedNodeId(null)}
            isAdvancedMode={isAdvancedMode}
            workflowId={params.id as string}
          />
        )}
      </div>

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
          if (executionId) router.push(`/app/executions/${executionId}`);
        }}
      />

      <ConfirmDialog
        open={showRunConfirm}
        title="Run workflow"
        message="This will run the workflow for real. Emails will be sent, sheets will be modified, and any connected services will be triggered. Continue?"
        confirmLabel="Run workflow"
        variant="warning"
        onConfirm={handleRealRun}
        onCancel={() => setShowRunConfirm(false)}
      />
    </div>
  );
}
