chrome.runtime.onInstalled.addListener(() => {
  console.log("PhishGuard installed");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "GET_ACTIVE_TAB_URL") {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0] ? tabs[0].url : null;
      sendResponse({ url });
    });
    return true;
  }
});