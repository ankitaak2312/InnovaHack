document.getElementById("scanBtn").addEventListener("click", () => {
  const resultDiv = document.getElementById("result");
  const riskScoreDiv = document.getElementById("riskScore");
  const explanationDiv = document.getElementById("explanation");

  resultDiv.classList.remove("hidden");
  riskScoreDiv.textContent = "...";
  explanationDiv.textContent = "Scanning...";

  chrome.runtime.sendMessage({ type: "SCAN_ACTIVE_TAB" }, (response) => {
    if (!response || response.error) {
      riskScoreDiv.textContent = "!";
      explanationDiv.textContent = response ? response.error : "Something went wrong";
      return;
    }

    const { risk_score } = response.data;
    riskScoreDiv.textContent = risk_score;
    explanationDiv.textContent = `Risk score: ${risk_score} / 100`;
  });
});