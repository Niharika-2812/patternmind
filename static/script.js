async function analyzeExperience() {

    const query = document.getElementById("query").value.trim();
    const result = document.getElementById("analysisResult");

    if (!query) {
        result.innerHTML = `
            <div class="result-box">
                <h3>Enter an experience</h3>
                <p>Describe an incident or event for PatternMind to analyze.</p>
            </div>
        `;
        return;
    }

    result.innerHTML = `
        <div class="result-box">
            <h3>◌ Analyzing memory...</h3>
            <p>Searching historical experiences and connecting related signals.</p>
        </div>
    `;

    const response = await fetch("/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            query: query
        })
    });

    const data = await response.json();

    if (!data.success) {
        result.innerHTML = `
            <div class="result-box">
                <h3>Error</h3>
                <p>${data.message}</p>
            </div>
        `;
        return;
    }

    let evidence = "";

    data.matches.forEach(match => {

        evidence += `
            <span>${match.experience.title}</span>
        `;

    });

    result.innerHTML = `
        <div class="result-box">

            <h3>✦ PatternMind Insight</h3>

            <p>
                ${data.insight}
            </p>

            <div class="evidence">

                <strong>Related memories:</strong>

                ${evidence || "<span>No direct historical match</span>"}

            </div>

        </div>
    `;
}