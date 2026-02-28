'use client';

import { useState, useEffect } from 'react';
import { X, Loader2, Sparkles, ChevronDown } from 'lucide-react';

interface SetupField {
  key: string;
  node_id: string | null;
  node_type: string | null;
  node_label: string | null;
  param_key: string;
  label: string;
  type: string;
  placeholder: string;
  required: boolean;
  options?: string[] | null;
  current_value?: string;
}

interface TemplateSetupWizardProps {
  open: boolean;
  templateName: string;
  fields: SetupField[];
  loading?: boolean;
  onSubmit: (values: Record<string, string>) => void;
  onCancel: () => void;
}

export default function TemplateSetupWizard({
  open,
  templateName,
  fields,
  loading = false,
  onSubmit,
  onCancel,
}: TemplateSetupWizardProps) {
  const [values, setValues] = useState<Record<string, string>>({});

  useEffect(() => {
    if (open) {
      // Pre-fill with current values from template
      const initial: Record<string, string> = {};
      fields.forEach(f => {
        if (f.current_value) initial[f.key] = f.current_value;
      });
      setValues(initial);
    }
  }, [open, fields]);

  if (!open) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(values);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') onCancel();
  };

  // Group fields: business-level first, then by node
  const businessFields = fields.filter(f => !f.node_id);
  const nodeFields = fields.filter(f => !!f.node_id);
  
  // Group node fields by node_label
  const nodeGroups: Record<string, SetupField[]> = {};
  nodeFields.forEach(f => {
    const group = f.node_label || f.node_type || 'Other';
    if (!nodeGroups[group]) nodeGroups[group] = [];
    nodeGroups[group].push(f);
  });

  const requiredFields = fields.filter(f => f.required);
  const allRequiredFilled = requiredFields.every(f => values[f.key]?.trim());

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onKeyDown={handleKeyDown}
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[85vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-5 h-5 text-primary-500" />
              <h2 className="text-lg font-semibold text-gray-900">Set Up Your Workflow</h2>
            </div>
            <p className="text-sm text-gray-500">{templateName}</p>
          </div>
          <button
            onClick={onCancel}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            <p className="text-sm text-gray-600">
              Configure the key settings for this workflow. You can always fine-tune everything later.
            </p>

            {/* Business-level fields */}
            {businessFields.length > 0 && (
              <div className="space-y-3">
                {businessFields.map(field => (
                  <FieldInput
                    key={field.key}
                    field={field}
                    value={values[field.key] || ''}
                    onChange={(val) => setValues(prev => ({ ...prev, [field.key]: val }))}
                  />
                ))}
              </div>
            )}

            {/* Node-grouped fields */}
            {Object.entries(nodeGroups).map(([groupLabel, groupFields]) => (
              <div key={groupLabel} className="space-y-3">
                <div className="flex items-center gap-2 pt-2">
                  <div className="h-px flex-1 bg-gray-100" />
                  <span className="text-xs text-gray-400 uppercase tracking-wide font-medium px-2">
                    {groupLabel}
                  </span>
                  <div className="h-px flex-1 bg-gray-100" />
                </div>
                {groupFields.map(field => (
                  <FieldInput
                    key={field.key}
                    field={field}
                    value={values[field.key] || ''}
                    onChange={(val) => setValues(prev => ({ ...prev, [field.key]: val }))}
                  />
                ))}
              </div>
            ))}

            {fields.length === 0 && (
              <p className="text-sm text-gray-400 text-center py-4">
                This template is ready to use as-is. Click create to get started.
              </p>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between gap-3 p-6 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !allRequiredFilled}
              className="px-6 py-2.5 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Workflow'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function FieldInput({
  field,
  value,
  onChange,
}: {
  field: SetupField;
  value: string;
  onChange: (val: string) => void;
}) {
  const baseClass = "w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-colors bg-white";

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        {field.label}
        {field.required && <span className="text-red-400 ml-0.5">*</span>}
      </label>
      {field.type === 'select' && field.options ? (
        <div className="relative">
          <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className={baseClass + " appearance-none pr-10"}
          >
            <option value="">Select...</option>
            {field.options.map(opt => (
              <option key={opt} value={opt}>
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      ) : field.type === 'textarea' ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          required={field.required}
          rows={3}
          className={baseClass + " resize-none"}
        />
      ) : (
        <input
          type={field.type === 'number' ? 'text' : field.type}
          inputMode={field.type === 'number' ? 'decimal' : undefined}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.placeholder}
          required={field.required}
          className={baseClass}
        />
      )}
      {field.current_value && value !== field.current_value && (
        <p className="text-xs text-gray-400 mt-1">Template default: {field.current_value}</p>
      )}
    </div>
  );
}
