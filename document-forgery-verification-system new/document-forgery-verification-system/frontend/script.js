async function uploadFile() {

    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a document to verify.");
        return;
    }

    const formData = new FormData();
    formData.append("document", file);

    const loading = document.getElementById("loading");
    const resultSection = document.getElementById("result");

    // Reset UI
    resultSection.classList.add("hidden");
    loading.classList.remove("hidden");

    try {

        const response = await fetch("/verify", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        loading.classList.add("hidden");

        if (!response.ok) {
            alert(data.error || "Verification failed.");
            return;
        }

        resultSection.classList.remove("hidden");

        /* ------------------------
           STATUS DISPLAY
        -------------------------*/
        const statusElement = document.getElementById("status");
        statusElement.innerText = "Result: " + data.status;

        if (data.status === "Genuine") {
            statusElement.style.color = "#28a745";
        } else if (data.status === "Suspicious") {
            statusElement.style.color = "#ff9800";
        } else {
            statusElement.style.color = "#dc3545";
        }

        /* ------------------------
           METRICS
        -------------------------*/
        document.getElementById("confidence").innerText = data.confidence;
        document.getElementById("ela_score").innerText = data.ela_score;

        /* ------------------------
           RISK SCORE
        -------------------------*/
        const riskElement = document.getElementById("risk_score");
        riskElement.innerText = data.risk_score + "%";

        if (data.risk_score < 30) {
            riskElement.className = "risk-low";
        } else if (data.risk_score < 60) {
            riskElement.className = "risk-medium";
        } else {
            riskElement.className = "risk-high";
        }

        /* ------------------------
           AI SUMMARY
        -------------------------*/
        document.getElementById("ai_summary").innerText =
            data.ai_summary || "No AI explanation available.";

        /* ------------------------
           METADATA
        -------------------------*/
        document.getElementById("metadata").innerText =
            data.metadata_analysis || "No metadata issues detected.";

        /* ------------------------
           DOCUMENT HASH
        -------------------------*/
        document.getElementById("document_hash").innerText =
            data.document_hash || "Hash not generated.";

        /* ------------------------
           EXTRACTED TEXT
        -------------------------*/
        document.getElementById("textPreview").innerText =
            data.extracted_text || "No readable text detected.";

        /* ------------------------
           HEATMAP IMAGE
        -------------------------*/
        document.getElementById("elaImage").src =
            "/uploads/" + data.ela_image;

        /* ------------------------
           REPORT DOWNLOAD
        -------------------------*/
        const reportLink = document.getElementById("reportLink");
        reportLink.href = "/uploads/" + data.report;
        reportLink.style.display = "inline-block";

    } catch (error) {
        loading.classList.add("hidden");
        alert("Server error. Please try again.");
        console.error(error);
    }
}