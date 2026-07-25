const API_BASE_URL = "https://innovahack-8q1t.onrender.com";

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

      // Render free-tier instances spin down when idle, so a cold start can
      // take 50+ seconds. Give it a generous timeout before giving up.
      const REQUEST_TIMEOUT_MS = 25000;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

      fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: activeUrl }),
        signal: controller.signal
      })
        .then((response) => {
          clearTimeout(timeoutId);
          if (!response.ok) {
            throw new Error(`status_${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          sendResponse({ data });
        })
        .catch((error) => {
          clearTimeout(timeoutId);
          if (error.name === "AbortError") {
            sendResponse({
              error: "Server Unreachable",
              detail: "The server took too long to respond. It may be waking up from sleep — please try scanning again in a moment."
            });
          } else if (error.message && error.message.startsWith("status_")) {
            sendResponse({
              error: "Server Unreachable",
              detail: `The server responded with an error (${error.message.replace("status_", "HTTP ")}). Please try again shortly.`
            });
          } else {
            sendResponse({
              error: "Server Unreachable",
              detail: "Couldn't reach the PhishGuard server. Check your connection and try again."
            });
          }
        });
    });

    return true;
  }
});