# Axon Web - Verification Checklist

Complete this checklist to verify all features are working correctly.

## Prerequisites

- [ ] Backend is running and accessible
- [ ] Frontend is running (`npm run dev`)
- [ ] JWT token obtained from backend

## 1. Settings Configuration ⚙️

Navigate to `/settings`

- [ ] Set Backend URL (e.g., `http://localhost:5000` or your Replit URL)
- [ ] Paste JWT Token from `/api/token/dev`
- [ ] Click "Save Settings" - should show success toast
- [ ] Click "Test Connection" - should show "Connection successful"
- [ ] Verify StatusPill in topbar shows "Connected"

## 2. Dashboard 📊

Navigate to `/`

- [ ] See "System Health" card with status, version, and timestamp
- [ ] See CPU usage card with percentage and progress bar
- [ ] See RAM usage card with used/total GB
- [ ] See Disk usage card with used/total GB
- [ ] See Uptime card with days/hours/minutes
- [ ] If GPU available: See GPU utilization and temperature cards
- [ ] Metrics refresh every 2 seconds automatically

## 3. Services 🖥️

Navigate to `/services`

- [ ] Services list loads successfully
- [ ] Search bar filters services by name
- [ ] Each service shows name, status badge, and type
- [ ] Click "Start" on a service - should show action toast
- [ ] Click "Stop" on a service - should show action toast
- [ ] Click "Restart" on a service - should show action toast
- [ ] Service list refreshes after control action

## 4. Commands 💻

Navigate to `/commands`

- [ ] Command input field accepts text
- [ ] Enter command `/usr/bin/ls -la`
- [ ] Optional: Set working directory
- [ ] Click "Run Command" - should show "Command started" toast
- [ ] Live terminal output appears in black console
- [ ] Output shows green text with command results
- [ ] Task ID displayed above terminal
- [ ] Click "Clear Logs" - terminal clears

## 5. Files 📁

Navigate to `/files`

- [ ] File browser shows current path
- [ ] Directory entries show folder icon
- [ ] File entries show file icon with size
- [ ] Click on directory - navigates into folder
- [ ] Current path updates in input field
- [ ] Click "Go Up" button - navigates to parent directory
- [ ] Click "Download" on a file - file downloads to browser
- [ ] Empty directories show "Directory is empty" message

## 6. Flows 🔄

Navigate to `/flows`

- [ ] Workflow ID input accepts text
- [ ] Payload textarea accepts JSON
- [ ] Invalid JSON shows error toast
- [ ] Enter workflow ID (e.g., `workflow-test`)
- [ ] Enter payload (e.g., `{"test": true}`)
- [ ] Click "Trigger Workflow" - shows success toast with runId
- [ ] Triggered workflow appears in "Recent Triggers" section
- [ ] Recent triggers show workflow ID, timestamp, and run ID

## 7. LLM Playground 🧠

Navigate to `/llm`

- [ ] Provider buttons show: openai, gemini, deepseek, ollama
- [ ] Click provider button - becomes active (highlighted)
- [ ] Enter prompt in textarea
- [ ] Click "Send to LLM" - button shows loading state
- [ ] Response appears in right panel
- [ ] Provider and model name shown above response
- [ ] Token usage displayed (if available)
- [ ] Try different providers

## 8. Chat & Voice 💬🎙️

Navigate to `/chat`

### Text Chat
- [ ] Chat panel loads with empty state
- [ ] Type message in input field
- [ ] Press Enter or click Send button
- [ ] User message appears (cyan bubble, right-aligned)
- [ ] Assistant response appears (magenta gradient bubble, left-aligned)
- [ ] Timestamps shown on messages
- [ ] Chat auto-scrolls to latest message
- [ ] Click "Limpiar" - clears all messages

### Voice Input
- [ ] Microphone button visible
- [ ] Click microphone - button turns red and pulses
- [ ] VU meter shows audio level bars
- [ ] Speak in Spanish
- [ ] Microphone stops - transcript appears in input field
- [ ] Can send transcribed text as message

### Text-to-Speech
- [ ] Toggle "Hablar respuesta" switch ON
- [ ] Send a message to agent
- [ ] Assistant response is spoken aloud
- [ ] Toggle switch OFF - responses not spoken

### Connection Status
- [ ] WebSocket status shows "Connected" in topbar
- [ ] If disconnected, shows "Conectando al servidor..."
- [ ] Send button disabled when not connected

## 9. UI/UX Details 🎨

### General
- [ ] Dark theme with #0b0f1a / #0f172a background
- [ ] Cyan/magenta neon accents throughout
- [ ] Rounded corners (rounded-2xl) on cards
- [ ] Glow effects on buttons and active elements
- [ ] Smooth transitions and hover effects

### Sidebar
- [ ] Sidebar shows "Axon Core" branding with glow
- [ ] Navigation items highlight on active page (cyan glow)
- [ ] Click collapse button - sidebar narrows to icons only
- [ ] Click expand button - sidebar shows full labels
- [ ] Hover effects on navigation items

### Topbar
- [ ] Shows "System Control Panel" title
- [ ] WebSocket status pill updates in real-time
- [ ] Connected = green, Disconnected = gray, Error = red

### Accessibility
- [ ] All interactive elements keyboard accessible (Tab navigation)
- [ ] Focus states visible on interactive elements
- [ ] Color contrast meets AA standards
- [ ] Toast notifications appear for all actions

## 10. Error Handling ❌

- [ ] Invalid JWT shows "Unauthorized" error
- [ ] Network errors show descriptive toast
- [ ] Backend unavailable shows connection failed
- [ ] Malformed requests show validation errors
- [ ] Empty required fields disable submit buttons

## Success Criteria ✅

All checkboxes should be checked for full verification.

If any checks fail:
1. Check browser console for errors
2. Verify backend is running and accessible
3. Confirm JWT token is valid and not expired
4. Check network tab for API responses
5. Review backend logs for errors

## Performance Checks

- [ ] Dashboard metrics update smoothly without lag
- [ ] Chat messages appear instantly
- [ ] Page transitions are smooth
- [ ] No console errors in browser DevTools
- [ ] WebSocket maintains connection during usage

---

**Verification Date**: _____________

**Verified By**: _____________

**Notes**: _____________
