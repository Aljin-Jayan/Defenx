// Default settings
const DEFAULT_SETTINGS = {
    apiUrl: 'http://127.0.0.1:8000',
    checkFrequency: 60,
    similarityThreshold: 0.95,
    takeScreenshots: true,
    sendNotifications: true
  };
  
  // State variables
  let currentUrl = '';
  let isMonitored = false;
  let currentStatus = 'unknown';
  let settings = { ...DEFAULT_SETTINGS };
  
  // DOM Elements
  const elements = {
    currentUrl: document.getElementById('current-url'),
    statusText: document.getElementById('status-text'),
    statusIndicator: document.getElementById('status-indicator'),
    statusBadgeText: document.getElementById('status-badge-text'),
    lastChecked: document.getElementById('last-checked'),
    initializeBtn: document.getElementById('initialize-btn'),
    checkBtn: document.getElementById('check-btn'),
    response: document.getElementById('response'),
    apiUrl: document.getElementById('api-url'),
    checkFrequency: document.getElementById('check-frequency'),
    similarityThreshold: document.getElementById('similarity-threshold'),
    takeScreenshots: document.getElementById('take-screenshots'),
    sendNotifications: document.getElementById('send-notifications'),
    saveSettingsBtn: document.getElementById('save-settings-btn'),
    resetSettingsBtn: document.getElementById('reset-settings-btn'),
    refreshStatusBtn: document.getElementById('refresh-status-btn'),
    monitoredSites: document.getElementById('monitored-sites'),
    alertContainer: document.getElementById('alert-container')
  };
  
  // Tab navigation
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      // Update active tab
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      // Show corresponding tab content
      document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
      document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
      
      // Load tab-specific data
      if (tab.dataset.tab === 'status') {
        loadMonitoredSites();
      }
    });
  });
  
  // Initialize
  document.addEventListener('DOMContentLoaded', async () => {
    // Load settings
    await loadSettings();
    
    // Fill settings form
    populateSettingsForm();
    
    // Get current URL
    getCurrentTabUrl();
    
    // Set up event listeners
    setupEventListeners();
    
    // Check if current site is monitored
    checkIfSiteIsMonitored();
  });
  
  // Set up event listeners
  function setupEventListeners() {
    // Monitor tab
    elements.initializeBtn.addEventListener('click', initializeMonitoring);
    elements.checkBtn.addEventListener('click', checkForDefacement);
    
    // Status tab
    elements.refreshStatusBtn.addEventListener('click', loadMonitoredSites);
    
    // Settings tab
    elements.saveSettingsBtn.addEventListener('click', saveSettings);
    elements.resetSettingsBtn.addEventListener('click', resetSettings);
  }
  
  // Get current tab URL
  function getCurrentTabUrl() {
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (tabs && tabs[0] && tabs[0].url) {
        currentUrl = tabs[0].url;
        elements.currentUrl.textContent = currentUrl;
        
        // Check if site is being monitored
        checkIfSiteIsMonitored();
      } else {
        elements.currentUrl.textContent = 'No active tab';
      }
    });
  }
  
  // Check if site is being monitored
  async function checkIfSiteIsMonitored() {
    if (!currentUrl) return;
    
    try {
      const response = await fetch(`${settings.apiUrl}/status?url=${encodeURIComponent(currentUrl)}`);
      
      if (response.ok) {
        const data = await response.json();
        isMonitored = true;
        updateMonitoringStatus(data);
        elements.checkBtn.disabled = false;
      } else if (response.status === 404) {
        // Site is not monitored
        isMonitored = false;
        updateNotMonitoredStatus();
      } else {
        // Error
        elements.response.textContent = 'Error checking monitoring status. API may be unavailable.';
      }
    } catch (error) {
      console.error('Error checking if site is monitored:', error);
      elements.response.textContent = `Error: ${error.message}`;
    }
  }
  
  // Initialize monitoring
  async function initializeMonitoring() {
    if (!currentUrl) return;
    
    // Update UI
    elements.initializeBtn.disabled = true;
    elements.initializeBtn.innerHTML = '<span class="spinner"></span>Starting...';
    elements.response.textContent = 'Initializing monitoring...';
    
    try {
      const response = await fetch(`${settings.apiUrl}/monitor`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: currentUrl,
          check_frequency: settings.checkFrequency * 60, // Convert to seconds
          similarity_threshold: settings.similarityThreshold,
          take_screenshots: settings.takeScreenshots,
          notify_email: settings.sendNotifications ? null : "" // Empty string disables notifications
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        elements.response.textContent = `Success: ${data.message}`;
        isMonitored = true;
        
        // Check status after a delay to let server process
        setTimeout(checkIfSiteIsMonitored, 1000);
      } else {
        elements.response.textContent = `Error: ${data.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Error initializing monitoring:', error);
      elements.response.textContent = `Error: ${error.message}`;
    } finally {
      // Reset button
      elements.initializeBtn.disabled = false;
      elements.initializeBtn.textContent = isMonitored ? 'Restart Monitoring' : 'Start Monitoring';
    }
  }
  
  // Check for defacement
  async function checkForDefacement() {
    if (!currentUrl) return;
    
    // Update UI
    elements.checkBtn.disabled = true;
    elements.checkBtn.innerHTML = '<span class="spinner"></span>Checking...';
    elements.response.textContent = 'Checking for defacement...';
    
    try {
      const response = await fetch(`${settings.apiUrl}/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: currentUrl
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        if (data.defacement_detected) {
          // Show alert
          showDefacementAlert(data);
          elements.response.textContent = `⚠️ DEFACEMENT DETECTED!\n\nReason: ${data.reason}\n\nContent similarity: ${(data.content_similarity * 100).toFixed(2)}%\nVisual similarity: ${data.visual_similarity ? (data.visual_similarity * 100).toFixed(2) + '%' : 'N/A'}`;
        } else {
          elements.response.textContent = `✓ No defacement detected.\n\nLast checked: ${new Date().toLocaleString()}`;
        }
        
        // Refresh status
        checkIfSiteIsMonitored();
      } else {
        elements.response.textContent = `Error: ${data.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Error checking for defacement:', error);
      elements.response.textContent = `Error: ${error.message}`;
    } finally {
      // Reset button
      elements.checkBtn.disabled = false;
      elements.checkBtn.textContent = 'Check Now';
    }
  }
  
  // Show defacement alert
  function showDefacementAlert(data) {
    const alertBox = document.createElement('div');
    alertBox.className = 'alert-box';
    
    alertBox.innerHTML = `
      <div class="alert-title">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FF9800" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
        Website Defacement Detected!
      </div>
      <div>The content of this website appears to have been modified maliciously.</div>
    `;
    
    // Remove previous alerts
    elements.alertContainer.innerHTML = '';
    elements.alertContainer.appendChild(alertBox);
    elements.alertContainer.style.display = 'block';
  }
  
  // Update monitoring status in UI
  function updateMonitoringStatus(data) {
    // Update button
    elements.initializeBtn.textContent = 'Restart Monitoring';
    elements.checkBtn.disabled = false;
    
    // Update status
    currentStatus = data.status || 'ok';
    elements.statusText.textContent = getStatusText(currentStatus);
    
    // Update indicator
    elements.statusIndicator.className = `status-indicator status-${getStatusClass(currentStatus)}`;
    elements.statusBadgeText.textContent = getStatusBadgeText(currentStatus);
    
    // Update last checked
    elements.lastChecked.textContent = data.last_checked ? 
      new Date(data.last_checked).toLocaleString() : 'Never';
    
    // Update response
    elements.response.textContent = `This website is being monitored.\nStatus: ${getStatusText(currentStatus)}\nMonitoring since: ${new Date(data.monitoring_since).toLocaleString()}`;
  }
  
  // Update UI for non-monitored sites
  function updateNotMonitoredStatus() {
    // Update button
    elements.initializeBtn.textContent = 'Start Monitoring';
    elements.checkBtn.disabled = true;
    
    // Update status
    currentStatus = 'unknown';
    elements.statusText.textContent = 'Not monitored';
    
    // Update indicator
    elements.statusIndicator.className = 'status-indicator status-unknown';
    elements.statusBadgeText.textContent = 'Not monitored';
    
    // Update last checked
    elements.lastChecked.textContent = 'Never';
    
    // Update response
    elements.response.textContent = 'This website is not being monitored. Click "Start Monitoring" to begin.';
  }
  
  // Load monitored sites
  async function loadMonitoredSites() {
    elements.monitoredSites.innerHTML = 'Loading...';
    
    try {
      const response = await fetch(`${settings.apiUrl}/status`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.length === 0) {
          elements.monitoredSites.innerHTML = '<p>No websites are currently being monitored.</p>';
        } else {
          const sitesHtml = data.map(site => {
            const statusClass = getStatusClass(site.status);
            const statusText = getStatusText(site.status);
            
            return `
              <div style="padding: 10px; border-bottom: 1px solid #eee; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                  <span class="status-indicator status-${statusClass}" style="margin-right: 5px;"></span>
                  <strong>${new URL(site.url).hostname}</strong>
                  <span style="margin-left: auto; font-size: 12px; color: #666;">
                    ${site.last_checked ? new Date(site.last_checked).toLocaleString() : 'Never checked'}
                  </span>
                </div>
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">${site.url}</div>
                <div style="font-size: 12px; display: flex; justify-content: space-between;">
                  <span>Status: ${statusText}</span>
                  <button class="check-site-btn" data-url="${site.url}" style="font-size: 11px; padding: 2px 6px;">Check</button>
                  <button class="stop-monitoring-btn" data-url="${site.url}" style="font-size: 11px; padding: 2px 6px; background-color: #f44336;">Stop</button>
                </div>
              </div>
            `;
          }).join('');
          
          elements.monitoredSites.innerHTML = sitesHtml;
          
          // Add event listeners to buttons
          document.querySelectorAll('.check-site-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
              const url = e.target.dataset.url;
              e.target.disabled = true;
              e.target.textContent = 'Checking...';
              
              try {
                await fetch(`${settings.apiUrl}/check`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ url })
                });
                
                // Refresh the list
                loadMonitoredSites();
              } catch (error) {
                console.error('Error checking site:', error);
              }
            });
          });
          
          document.querySelectorAll('.stop-monitoring-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
              if (confirm('Are you sure you want to stop monitoring this website?')) {
                const url = e.target.dataset.url;
                e.target.disabled = true;
                e.target.textContent = 'Stopping...';
                
                try {
                  await fetch(`${settings.apiUrl}/stop`, {
                    method: 'DELETE',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                  });
                  
                  // Refresh the list
                  loadMonitoredSites();
                  
                  // If this was the current URL, update UI
                  if (url === currentUrl) {
                    updateNotMonitoredStatus();
                  }
                } catch (error) {
                  console.error('Error stopping monitoring:', error);
                }
              }
            });
          });
        }
      } else {
        elements.monitoredSites.innerHTML = '<p>Error loading monitored websites. API may be unavailable.</p>';
      }
    } catch (error) {
      console.error('Error loading monitored sites:', error);
      elements.monitoredSites.innerHTML = `<p>Error: ${error.message}</p>`;
    }
  }
  
  // Load settings from storage
  async function loadSettings() {
    return new Promise(resolve => {
      chrome.storage.sync.get('defacementDetectorSettings', (data) => {
        if (data.defacementDetectorSettings) {
          settings = { ...DEFAULT_SETTINGS, ...data.defacementDetectorSettings };
        } else {
          settings = { ...DEFAULT_SETTINGS };
        }
        resolve(settings);
      });
    });
  }
  
  // Save settings to storage
  async function saveSettings() {
    // Get values from form
    settings.apiUrl = elements.apiUrl.value;
    settings.checkFrequency = parseInt(elements.checkFrequency.value);
    settings.similarityThreshold = parseFloat(elements.similarityThreshold.value);
    settings.takeScreenshots = elements.takeScreenshots.checked;
    settings.sendNotifications = elements.sendNotifications.checked;
    
    // Validate
    if (!settings.apiUrl) {
      alert('API URL is required');
      return;
    }
    
    if (isNaN(settings.checkFrequency) || settings.checkFrequency < 5) {
      alert('Check frequency must be at least 5 minutes');
      return;
    }
    
    if (isNaN(settings.similarityThreshold) || settings.similarityThreshold < 0.5 || settings.similarityThreshold > 1) {
      alert('Similarity threshold must be between 0.5 and 1.0');
      return;
    }
    
    // Save to storage
    chrome.storage.sync.set({ defacementDetectorSettings: settings }, () => {
      elements.response.textContent = 'Settings saved successfully.';
      
      // Switch to monitor tab
      document.querySelector('.tab[data-tab="monitor"]').click();
      
      // Refresh status to apply new settings
      checkIfSiteIsMonitored();
    });
  }
  
  // Reset settings to defaults
  function resetSettings() {
    if (confirm('Reset all settings to default values?')) {
      settings = { ...DEFAULT_SETTINGS };
      populateSettingsForm();
      
      // Save to storage
      chrome.storage.sync.set({ defacementDetectorSettings: settings }, () => {
        elements.response.textContent = 'Settings reset to defaults.';
      });
    }
  }
  
  // Fill settings form with current values
  function populateSettingsForm() {
    elements.apiUrl.value = settings.apiUrl;
    elements.checkFrequency.value = settings.checkFrequency;
    elements.similarityThreshold.value = settings.similarityThreshold;
    elements.takeScreenshots.checked = settings.takeScreenshots;
    elements.sendNotifications.checked = settings.sendNotifications;
  }
  
  // Helper functions
  function getStatusClass(status) {
    switch (status) {
      case 'ok':
        return 'ok';
      case 'defaced':
        return 'error';
      case 'initializing':
        return 'warning';
      default:
        return 'unknown';
    }
  }
  
  function getStatusText(status) {
    switch (status) {
      case 'ok':
        return 'Secure';
      case 'defaced':
        return 'Defaced';
      case 'initializing':
        return 'Initializing';
      default:
        return 'Unknown';
    }
  }
  
  function getStatusBadgeText(status) {
    switch (status) {
      case 'ok':
        return 'Monitored';
      case 'defaced':
        return 'DEFACED';
      case 'initializing':
        return 'Initializing';
      default:
        return 'Not monitored';
    }
  }