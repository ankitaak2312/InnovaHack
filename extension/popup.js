document.getElementById("scanBtn").addEventListener("click", () => {
  const resultDiv = document.getElementById("result");
  const gaugeDiv = document.getElementById("gauge");
  const riskScoreDiv = document.getElementById("riskScore");
  const riskLevelDiv = document.getElementById("riskLevel");
  const explanationDiv = document.getElementById("explanation");

  resultDiv.classList.remove("hidden");
  gaugeDiv.className = "gauge";
  riskScoreDiv.textContent = "...";
  riskLevelDiv.textContent = "";
  explanationDiv.innerHTML = "Scanning...";

  chrome.runtime.sendMessage({ type: "SCAN_ACTIVE_TAB" }, (response) => {
    if (!response || response.error) {
      gaugeDiv.className = "gauge phishing";
      riskScoreDiv.textContent = "!";
      riskLevelDiv.textContent = "ERROR";
      explanationDiv.innerHTML = response ? response.error : "Something went wrong";
      return;
    }

    const { risk_score, risk_level, flags } = response.data;

    gaugeDiv.className = `gauge ${risk_level}`;
    riskScoreDiv.textContent = risk_score;
    riskLevelDiv.textContent = risk_level;

    if (flags && flags.length > 0) {
      const listItems = flags.map((flag) => `<li>${flag}</li>`).join("");
      explanationDiv.innerHTML = `<ul>${listItems}</ul>`;
    } else {
      explanationDiv.innerHTML = "No red flags detected.";
    }
  });
});