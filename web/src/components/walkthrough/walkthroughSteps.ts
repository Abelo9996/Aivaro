import type { WalkthroughStep } from './Walkthrough';

export const WALKTHROUGH_STEPS: WalkthroughStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to Aivaro! 🎉',
    description:
      "Let's take a quick tour to help you get the most out of your automation platform. This will only take a minute!",
    position: 'center',
    path: '/app',
  },
  {
    id: 'dashboard-overview',
    title: 'Your Dashboard',
    description:
      'This is your home base. See pending approvals, quick actions, and your workflows at a glance. Everything you need is one click away.',
    targetSelector: '[data-walkthrough="dashboard"]',
    position: 'bottom',
    spotlightPadding: 12,
    path: '/app',
  },
  {
    id: 'workflows-intro',
    title: 'Your Workflows',
    description:
      "Let's check out where your automations live. Click Next to see the Workflows page.",
    targetSelector: '[data-walkthrough="nav-workflows"]',
    position: 'right',
    spotlightPadding: 4,
    path: '/app',
  },
  {
    id: 'workflows-page',
    title: 'Workflows Page',
    description:
      'Here you can see all your automations. Each workflow has steps that run automatically when triggered - like a recipe for your business!',
    targetSelector: '[data-walkthrough="workflows-list"]',
    position: 'bottom',
    spotlightPadding: 12,
    path: '/app/workflows',
  },
  {
    id: 'workflows-create',
    title: 'Create New Workflow',
    description:
      'Click this button anytime to create a new automation from scratch. But first, let me show you something easier...',
    targetSelector: '[data-walkthrough="create-workflow-btn"]',
    position: 'bottom',
    spotlightPadding: 8,
    path: '/app/workflows',
  },
  {
    id: 'templates-intro',
    title: 'Templates Library',
    description:
      "Don't want to start from scratch? We have pre-built automations ready to use. Let's check them out!",
    targetSelector: '[data-walkthrough="nav-templates"]',
    position: 'right',
    spotlightPadding: 4,
    path: '/app/workflows',
  },
  {
    id: 'templates-page',
    title: 'Browse Templates',
    description:
      'Pick any template that fits your business. Each one is ready to use - just customize it and turn it on!',
    targetSelector: '[data-walkthrough="templates-grid"]',
    position: 'top',
    spotlightPadding: 12,
    path: '/app/templates',
  },
  {
    id: 'templates-use',
    title: 'Use a Template',
    description:
      'Found one you like? Click "Use Template" and it becomes your workflow instantly. You can customize it later.',
    targetSelector: '[data-walkthrough="template-card"]',
    position: 'right',
    spotlightPadding: 8,
    path: '/app/templates',
  },
  {
    id: 'executions-intro',
    title: 'Run History',
    description:
      "Now let's see where you track what your automations have done.",
    targetSelector: '[data-walkthrough="nav-executions"]',
    position: 'right',
    spotlightPadding: 4,
    path: '/app/templates',
  },
  {
    id: 'executions-page',
    title: 'Execution History',
    description:
      'Every time a workflow runs, it shows up here. See what happened, when it ran, and if there were any issues. Full transparency!',
    targetSelector: '[data-walkthrough="executions-list"]',
    position: 'bottom',
    spotlightPadding: 12,
    path: '/app/executions',
  },
  {
    id: 'connections-intro',
    title: 'Connect Your Apps',
    description:
      "Your automations need to talk to your apps. Let's set up connections.",
    targetSelector: '[data-walkthrough="nav-connections"]',
    position: 'right',
    spotlightPadding: 4,
    path: '/app/executions',
  },
  {
    id: 'connections-page',
    title: 'Your Connections',
    description:
      'Connect Google Sheets, Gmail, Slack, and more. Once connected, all your workflows can use them. Set it once, use everywhere!',
    targetSelector: '[data-walkthrough="connections-grid"]',
    position: 'bottom',
    spotlightPadding: 12,
    path: '/app/connections',
  },
  {
    id: 'approvals-intro',
    title: 'Stay in Control',
    description:
      "Some actions need your approval before running. Let's see where those requests go.",
    targetSelector: '[data-walkthrough="nav-approvals"]',
    position: 'right',
    spotlightPadding: 4,
    path: '/app/connections',
  },
  {
    id: 'approvals-page',
    title: 'Approval Center',
    description:
      'When a workflow needs your OK (like sending an important email), the request appears here. Review it, approve or reject - you\'re always in control.',
    targetSelector: '[data-walkthrough="approvals-list"]',
    position: 'bottom',
    spotlightPadding: 12,
    path: '/app/approvals',
  },
  {
    id: 'finish',
    title: "You're All Set! 🚀",
    description:
      "That's the tour! Start by browsing Templates to find your first automation, or create one from scratch. Need help? Click the ❓ Help button anytime.",
    position: 'center',
    path: '/app',
  },
];

export const WALKTHROUGH_STORAGE_KEY = 'aivaro_walkthrough_completed';
