const API_BASE_URL = "http://localhost:8000";

chrome.runtime.onInstalled.addListener(() => {
  console.log("PhishGuard installed");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "SCAN_ACTIVE_TAB") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeUrl = tabs[0] ? tabs[0].url : null;

      if (!activeUrl) {
        sendResponse({ error: "Unable to read active tab URL" });
        return;
      }

      fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: activeUrl })
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`API responded with status ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          sendResponse({ data });
        })
        .catch((error) => {
          sendResponse({ error: error.message });
        });
    });

    return true;
  }
});