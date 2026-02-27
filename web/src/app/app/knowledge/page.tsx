'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import {
  Info, Plus, Pencil, Trash2, X, Check, Upload,
  Building2, DollarSign, ShieldCheck, Users,
  CalendarClock, TrendingUp, HelpCircle, Mail, Tag, FileText
} from 'lucide-react';
import { api } from '@/lib/api';

interface KnowledgeEntry {
  id: string;
  category: string;
  title: string;
  content: string;
  priority: number;
  created_at: string;
  updated_at: string;
}

interface Category {
  id: string;
  description: string;
}

const CATEGORY_ICONS: Record<string, any> = {
  business_info: Building2,
  pricing: DollarSign,
  policies: ShieldCheck,
  contacts: Users,
  deadlines: CalendarClock,
  financials: TrendingUp,
  faq: HelpCircle,
  email_templates: Mail,
  custom: Tag,
};

const CATEGORY_COLORS: Record<string, string> = {
  business_info: 'bg-blue-50 text-blue-700 border-blue-200',
  pricing: 'bg-green-50 text-green-700 border-green-200',
  policies: 'bg-purple-50 text-purple-700 border-purple-200',
  contacts: 'bg-orange-50 text-orange-700 border-orange-200',
  deadlines: 'bg-red-50 text-red-700 border-red-200',
  financials: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  faq: 'bg-amber-50 text-amber-700 border-amber-200',
  email_templates: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  custom: 'bg-gray-50 text-gray-700 border-gray-200',
};

const CATEGORY_LABELS: Record<string, string> = {
  business_info: 'Business Info',
  pricing: 'Pricing',
  policies: 'Policies',
  contacts: 'Contacts',
  deadlines: 'Deadlines',
  financials: 'Financials',
  faq: 'FAQ',
  email_templates: 'Email Templates',
  custom: 'Other',
};

export default function KnowledgePage() {
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ category: 'business_info', title: '', content: '', priority: 0 });
  const [saving, setSaving] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    loadEntries();
  }, [activeCategory]);

  const loadData = async () => {
    try {
      const [cats] = await Promise.all([api.getKnowledgeCategories()]);
      setCategories(cats);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
    await loadEntries();
  };

  const loadEntries = async () => {
    try {
      const data = await api.getKnowledge(activeCategory || undefined);
      setEntries(data);
    } catch (err) {
      console.error('Failed to load knowledge:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!form.title.trim() || !form.content.trim()) return;
    setSaving(true);
    try {
      if (editingId) {
        await api.updateKnowledge(editingId, form);
      } else {
        await api.createKnowledge(form);
      }
      setShowForm(false);
      setEditingId(null);
      setForm({ category: 'business_info', title: '', content: '', priority: 0 });
      await loadEntries();
    } catch (err) {
      console.error('Failed to save:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (entry: KnowledgeEntry) => {
    setForm({
      category: entry.category,
      title: entry.title,
      content: entry.content,
      priority: entry.priority,
    });
    setEditingId(entry.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this knowledge entry?')) return;
    try {
      await api.deleteKnowledge(id);
      await loadEntries();
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const handleFileImport = async (file: File) => {
    setImporting(true);
    setImportResult(null);
    try {
      const entries = await api.importKnowledgeFile(file);
      await loadEntries();
      setImportResult(`Imported ${entries.length} knowledge ${entries.length === 1 ? 'entry' : 'entries'} from "${file.name}"`);
      setTimeout(() => setImportResult(null), 5000);
    } catch (err: any) {
      setImportResult(`Failed: ${err.message}`);
      setTimeout(() => setImportResult(null), 5000);
    } finally {
      setImporting(false);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFileImport(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  // Group entries by category
  const grouped = entries.reduce((acc, e) => {
    acc[e.category] = acc[e.category] || [];
    acc[e.category].push(e);
    return acc;
  }, {} as Record<string, KnowledgeEntry[]>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading knowledge base...</div>
      </div>
    );
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className="relative"
    >
      {/* Drag overlay */}
      {isDragging && (
        <div className="fixed inset-0 z-50 bg-primary-600/10 backdrop-blur-sm flex items-center justify-center pointer-events-none">
          <div className="bg-white rounded-2xl border-2 border-dashed border-primary-400 p-12 text-center shadow-xl">
            <Upload className="w-12 h-12 text-primary-500 mx-auto mb-4" />
            <p className="text-lg font-semibold text-gray-900">Drop file to import</p>
            <p className="text-sm text-gray-500 mt-1">PDF, TXT, CSV, DOCX, MD, JSON, HTML</p>
          </div>
        </div>
      )}

      {/* Import result toast */}
      {importResult && (
        <div className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm font-medium ${
          importResult.startsWith('Failed') ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
        }`}>
          {importResult}
        </div>
      )}

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
          <p className="text-gray-500">
            Teach Aivaro about your business. This context is used when replying to emails, creating workflows, and running tasks.
          </p>
        </div>
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            accept=".txt,.md,.csv,.json,.pdf,.doc,.docx,.rtf,.html,.htm"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileImport(file);
              e.target.value = '';
            }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={importing}
            className="flex items-center gap-2 px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium disabled:opacity-50"
          >
            {importing ? (
              <>
                <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                Importing...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Import File
              </>
            )}
          </button>
          <button
            onClick={() => {
              setForm({ category: activeCategory || 'business_info', title: '', content: '', priority: 0 });
              setEditingId(null);
              setShowForm(true);
            }}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium"
          >
            <Plus className="w-4 h-4" />
            Add Knowledge
          </button>
        </div>
      </div>

      {/* Category Filters */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button
          onClick={() => setActiveCategory(null)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
            !activeCategory
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'
          }`}
        >
          All ({entries.length})
        </button>
        {categories.map((cat) => {
          const count = entries.filter(e => e.category === cat.id).length;
          const Icon = CATEGORY_ICONS[cat.id] || Tag;
          return (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(activeCategory === cat.id ? null : cat.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                activeCategory === cat.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {CATEGORY_LABELS[cat.id] || cat.id}
              {count > 0 && <span className="text-xs opacity-70">({count})</span>}
            </button>
          );
        })}
      </div>

      {/* Add/Edit Form */}
      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h3 className="font-semibold mb-4">{editingId ? 'Edit Entry' : 'Add Knowledge'}</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  value={form.category}
                  onChange={(e) => setForm({ ...form, category: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {CATEGORY_LABELS[cat.id] || cat.id} — {cat.description}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                <select
                  value={form.priority}
                  onChange={(e) => setForm({ ...form, priority: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value={0}>Normal</option>
                  <option value={1}>High — always included in AI context</option>
                  <option value={2}>Critical — shown first</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="e.g., Cancellation Policy, Standard Pricing, Business Hours"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
              <textarea
                value={form.content}
                onChange={(e) => setForm({ ...form, content: e.target.value })}
                placeholder="Write what Aivaro should know. Be specific — this is used when replying to emails, running tasks, and creating workflows."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleSave}
                disabled={saving || !form.title.trim() || !form.content.trim()}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium disabled:opacity-50"
              >
                <Check className="w-4 h-4" />
                {saving ? 'Saving...' : editingId ? 'Update' : 'Save'}
              </button>
              <button
                onClick={() => { setShowForm(false); setEditingId(null); }}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm font-medium"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Entries */}
      {entries.length === 0 ? (
        <div
          className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-12 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/30 transition"
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="text-5xl mb-4">🧠</div>
          <h3 className="text-lg font-semibold mb-2">Your knowledge base is empty</h3>
          <p className="text-gray-500 mb-4 max-w-md mx-auto">
            Add information about your business so Aivaro can write better emails,
            create smarter workflows, and handle tasks with full context.
          </p>
          <div className="flex items-center justify-center gap-4 mb-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 rounded-lg text-sm font-medium">
              <Upload className="w-4 h-4" />
              Drop a file or click to import
            </div>
          </div>
          <div className="text-sm text-gray-400 space-y-1">
            <p>Supports PDF, TXT, CSV, DOCX, MD, JSON, HTML files</p>
            <p>Or manually add: business hours, pricing, cancellation policy, FAQ answers</p>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([category, items]) => {
            const Icon = CATEGORY_ICONS[category] || Tag;
            const colorClass = CATEGORY_COLORS[category] || CATEGORY_COLORS.custom;
            return (
              <div key={category}>
                <div className="flex items-center gap-2 mb-3">
                  <div className={`p-1.5 rounded ${colorClass}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <h2 className="font-semibold text-gray-800">
                    {CATEGORY_LABELS[category] || category}
                  </h2>
                  <span className="text-xs text-gray-400">{items.length} entries</span>
                </div>
                <div className="space-y-2">
                  {items.map((entry) => (
                    <div
                      key={entry.id}
                      className="bg-white rounded-lg border border-gray-200 p-4 group"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-gray-900">{entry.title}</span>
                            {entry.priority > 0 && (
                              <span className={`px-1.5 py-0.5 text-xs rounded ${
                                entry.priority >= 2 ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'
                              }`}>
                                {entry.priority >= 2 ? 'Critical' : 'High'}
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 whitespace-pre-wrap">{entry.content}</p>
                        </div>
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition ml-4">
                          <button
                            onClick={() => handleEdit(entry)}
                            className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(entry.id)}
                            className="p-1.5 text-gray-400 hover:text-red-600 rounded"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
          <Info className="w-4 h-4" />
          How it works
        </h3>
        <p className="text-sm text-blue-700 mb-2">
          Everything you add here becomes context that Aivaro uses when:
        </p>
        <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
          <li><strong>Replying to emails</strong> — knows your pricing, policies, hours</li>
          <li><strong>Running agent tasks</strong> — knows who to contact, what to say</li>
          <li><strong>Building workflows</strong> — suggests steps that match your business</li>
          <li><strong>Chatting with you</strong> — understands your business context</li>
        </ul>
        <p className="text-sm text-blue-600 mt-3">
          <strong>Tip:</strong> Drag and drop files (PDF, TXT, CSV, DOCX) to auto-import business documents.
        </p>
      </div>
    </div>
  );
}
