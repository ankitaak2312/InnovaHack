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
      riskLevelDiv.textContent = response && response.error ? response.error : "ERROR";
      const detail =
        response && response.detail
          ? response.detail
          : "Something went wrong. Please try again.";
      explanationDiv.innerHTML = `<p class="explanation-text">${detail}</p>`;
      return;
    }

    const { risk_score, risk_level, explanation, flags } = response.data;

    gaugeDiv.className = `gauge ${risk_level}`;
    riskScoreDiv.textContent = risk_score;
    riskLevelDiv.textContent = risk_level;

    let html = `<p class="explanation-text">${explanation}</p>`;
    if (flags && flags.length > 0) {
      const listItems = flags.map((flag) => `<li>${flag}</li>`).join("");
      html += `<ul>${listItems}</ul>`;
    }
    explanationDiv.innerHTML = html;
  });
});