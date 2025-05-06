// Default settings
const DEFAULT_SETTINGS = {
    apiUrl: 'http://127.0.0.1:8000',
    checkFrequency: 60,
    similarityThreshold: 0.95,
    takeScreenshots: true,
    sendNotifications: true
  };
  
  // Global variables
  let settings = { ...DEFAULT_SETTINGS };
  let monitoredSites = {};
  let checkIntervals = {};
  
  // Initialize extension
  chrome.runtime.onInstalled.addListener(async () => {
    console.log("Website Defacement Monitor Extension installed!");
    
    // Load settings
    await loadSettings();
    
    // Set up alarm for periodic checks
    setupAlarm();
    
    // Load monitored sites
    await loadMonitoredSites();
  });
  
  // Listen for alarm
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'checkMonitoredSites') {
      checkAllMonitoredSites();
    }
  });
  
  // Set up alarm for periodic checks
  function setupAlarm() {
    chrome.alarms.clear('checkMonitoredSites');
    
    chrome.alarms.create('checkMonitoredSites', {
      periodInMinutes: settings.checkFrequency
    });
    
    console.log(`Scheduled checks every ${settings.checkFrequency} minutes`);
  }
  
  // Load settings from storage
  async function loadSettings() {
    return new Promise(resolve => {
      chrome.storage.sync.get('defacementDetectorSettings', (data) => {
        if (data.defacementDetectorSettings) {
          settings = { ...DEFAULT_SETTINGS, ...data.defacementDetectorSettings };
        }
        resolve(settings);
      });
    });
  }
  
  // Load monitored sites
  async function loadMonitoredSites() {
    try {
      const response = await fetch(`${settings.apiUrl}/status`);
      
      if (response.ok) {
        const sites = await response.json();
        monitoredSites = {};
        
        sites.forEach(site => {
          monitoredSites[site.url] = site;
        });
        
        console.log(`Loaded ${sites.length} monitored sites`);
      } else {
        console.error('Error loading monitored sites', await response.text());
      }
    } catch (error) {
      console.error('Error loading monitored sites:', error);
    }
  }
  
  // Check all monitored sites
  async function checkAllMonitoredSites() {
    console.log('Checking all monitored sites...');
    
    // Reload settings first
    await loadSettings();
    
    // Get the current list of monitored sites
    await loadMonitoredSites();
    
    // No sites to check
    if (Object.keys(monitoredSites).length === 0) {
      console.log('No sites to check');
      return;
    }
    
    // Check each site
    for (const url of Object.keys(monitoredSites)) {
      await checkSite(url);
    }
  }
  
  // Check a single site for defacement
  async function checkSite(url) {
    console.log(`Checking site: ${url}`);
    
    try {
      const response = await fetch(`${settings.apiUrl}/check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url })
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Update site status
        if (monitoredSites[url]) {
          monitoredSites[url].status = data.defacement_detected ? 'defaced' : 'ok';
          monitoredSites[url].last_checked = data.checked_at;
        }
        
        // Show notification if defacement detected
        if (data.defacement_detected) {
          showDefacementNotification(url, data.reason);
        }
        
        console.log(`Check completed for ${url}. Status: ${data.defacement_detected ? 'DEFACED' : 'OK'}`);
      } else {
        console.error(`Error checking ${url}:`, await response.text());
      }
    } catch (error) {
      console.error(`Error checking ${url}:`, error);
    }
  }
  
  // Show a notification for defacement
  function showDefacementNotification(url, reason) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/deface128.png',
      title: '⚠️ Website Defacement Detected!',
      message: `Potential defacement detected on ${url}. ${reason.substring(0, 100)}${reason.length > 100 ? '...' : ''}`,
      priority: 2
    });
  }
  
  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'getSettings') {
      sendResponse(settings);
    }
    
    if (message.action === 'saveSettings') {
      settings = message.settings;
      chrome.storage.sync.set({ defacementDetectorSettings: settings });
      setupAlarm();
      sendResponse({ success: true });
    }
    
    if (message.action === 'checkSite') {
      checkSite(message.url)
        .then(() => sendResponse({ success: true }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true; // Required for async response
    }
    
    if (message.action === 'checkAllSites') {
      checkAllMonitoredSites()
        .then(() => sendResponse({ success: true }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true; // Required for async response
    }
  });