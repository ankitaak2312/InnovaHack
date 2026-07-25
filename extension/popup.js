document.getElementById("scanBtn").addEventListener("click", () => {
  const resultDiv = document.getElementById("result");
  const riskScoreDiv = document.getElementById("riskScore");
  const explanationDiv = document.getElementById("explanation");

  chrome.runtime.sendMessage({ type: "GET_ACTIVE_TAB_URL" }, (response) => {
    resultDiv.classList.remove("hidden");
    riskScoreDiv.textContent = "??";
    explanationDiv.textContent = response.url ? response.url : "Unable to read tab URL";
  });
});