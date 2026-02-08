# Happy Path: Create Your First Automation

This guide walks you through creating, testing, and running your first workflow in Aivaro.

## Step 1: Sign Up & Onboarding

1. Go to http://localhost:3000/signup
2. Create an account with email and password
3. Complete the onboarding wizard:
   - Select "Service Business" as your business type
   - Choose "Booking → deposit → reminders" template
   - Skip connection setup (we'll use mock connections)

## Step 2: Explore the Workflow

After onboarding, you'll land on the workflow builder:

1. **Canvas** (center): You'll see your workflow with connected steps
2. **What will happen panel** (top): Plain English summary of the workflow
3. **Node Palette** (left): Available steps you can add
4. **Inspector** (right): Click any step to configure it

The workflow shows:
- **Start**: When a booking form is submitted
- **Send Email**: Send deposit request email ⚠️ (requires approval)
- **Wait**: Wait 24 hours
- **Send Email**: Send reminder if no payment

## Step 3: Test Run

1. Click the **"Test Run"** button (green button, top right)
2. A panel slides in showing:
   - "This will use mock data"
   - "No real emails will be sent"
   - Preview of test data
3. Click **"Run Test"**
4. Watch the execution progress through each step
5. When it reaches "Send deposit email", it pauses for approval

## Step 4: Approve the Email

1. The approval modal appears showing:
   - **What will happen**: "Send an email to test@example.com"
   - **Subject**: "Deposit Required for Your Booking"
   - **Preview of email content**
2. Review the details
3. Click **"Approve & Continue"**
4. The workflow continues to completion

## Step 5: View Run History

1. Go to **Run History** in the sidebar
2. Find your test run (marked with "Test" badge)
3. Click to see the execution timeline:
   - Each step shows status (✓ completed)
   - Time taken for each step
   - Input/output data
   - The approval action you took

## Step 6: Turn It On

1. Go back to **Workflows** > your workflow
2. Toggle **"Turn on"** at the top
3. Your workflow is now active!

## What Happens in Production

When a real booking form is submitted:
1. Aivaro captures the form data
2. Prepares the deposit email
3. **Pauses and notifies you** (email + dashboard notification)
4. You review and approve in the Approvals page
5. Email is sent, workflow continues
6. After 24 hours, reminder is sent automatically (if configured as safe)

---

## Troubleshooting

**Workflow not saving?**
- Check browser console for errors
- Ensure API is running on port 8000

**Test run stuck?**
- Check the Approvals page for pending items
- Refresh the page

**Database connection issues?**
- Ensure Docker is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
