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
import { useWorkflowStore } from '@/stores/workflowStore';
import { useModeStore } from '@/stores/modeStore';
import NodePalette from '@/components/workflow/NodePalette';
import NodeInspector from '@/components/workflow/NodeInspector';
import TriggerNode from '@/components/workflow/nodes/TriggerNode';
import ActionNode from '@/components/workflow/nodes/ActionNode';
import ConditionNode from '@/components/workflow/nodes/ConditionNode';
import ApprovalNode from '@/components/workflow/nodes/ApprovalNode';
import type { Workflow, WorkflowNode } from '@/types';

const nodeTypes = {
  trigger: TriggerNode,
  action: ActionNode,
  condition: ConditionNode,
  approval: ApprovalNode,
};

export default function WorkflowEditorPage() {
  const params = useParams();
  const router = useRouter();
  const { isAdvancedMode } = useModeStore();
  const { setCurrentWorkflow, currentWorkflow } = useWorkflowStore();
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [showPalette, setShowPalette] = useState(false);
  const [workflowName, setWorkflowName] = useState('New Workflow');

  const workflowId = params.id as string;
  const isNew = workflowId === 'new';

  useEffect(() => {
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
      loadWorkflow(workflowId);
    }
  }, [workflowId, isNew]);

  const loadWorkflow = async (id: string) => {
    try {
      const workflow = await api.getWorkflow(id);
      setCurrentWorkflow(workflow);
      setWorkflowName(workflow.name);
      
      // Convert workflow nodes to React Flow nodes
      const flowNodes: Node[] = workflow.nodes.map((node: WorkflowNode) => ({
        id: node.id,
        type: node.type === 'trigger' ? 'trigger' : 
              node.type === 'condition' ? 'condition' :
              node.type === 'approval' ? 'approval' : 'action',
        position: node.position || { x: 100, y: 100 },
        data: {
          label: node.label || node.type,
          nodeType: node.type,
          config: node.config || {},
        },
      }));
      
      // Convert workflow edges
      const flowEdges: Edge[] = workflow.edges.map((edge: any) => ({
        id: edge.id || `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
      }));
      
      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (err) {
      console.error('Failed to load workflow:', err);
    } finally {
      setLoading(false);
    }
  };

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
          config: n.data.config || {},
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

  const handleTestRun = async () => {
    try {
      const execution = await api.runWorkflow(workflowId, true); // isTest = true
      router.push(`/app/executions/${execution.id}`);
    } catch (err) {
      console.error('Failed to run test:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500">Loading workflow...</div>
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
            <button
              onClick={handleTestRun}
              className="px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100"
            >
              🧪 Test Run
            </button>
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
          />
        )}
      </div>
    </div>
  );
}
