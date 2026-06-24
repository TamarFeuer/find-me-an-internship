// Mirrors the Match model the backend returns from POST /matches.
interface Match {
  title: string;
  company: string | null;
  location: string | null;
  url: string | null;
  score: number;
  explanation: string;
}

const button = document.getElementById("find-btn") as HTMLButtonElement;
const statusEl = document.getElementById("status") as HTMLParagraphElement;
const results = document.getElementById("results") as HTMLUListElement;
const fileInput = document.getElementById("cv-file") as HTMLInputElement;
const fileName = document.getElementById("file-name") as HTMLSpanElement;
const whatInput = document.getElementById("what") as HTMLInputElement;
const whereInput = document.getElementById("where") as HTMLInputElement;
const excludeInput = document.getElementById("exclude") as HTMLInputElement;

// Show the chosen file's name next to the upload button.
fileInput.addEventListener("change", () => {
  fileName.textContent = fileInput.files?.[0]?.name ?? "";
});

button.addEventListener("click", async () => {
  // The user must pick a PDF before we can score anything.
  const file = fileInput.files?.[0];
  if (!file) {
    statusEl.textContent = "Please choose a PDF CV first.";
    return;
  }

  // Disable the button and show progress while the (slow) scoring runs.
  button.disabled = true;
  statusEl.textContent = "Scoring jobs… this takes a few seconds.";
  results.innerHTML = "";

  try {
    // Send the PDF as multipart form data; the field name "cv" matches the backend.
    const formData = new FormData();
    formData.append("cv", file);
    formData.append("what", whatInput.value);
    formData.append("where", whereInput.value);
    formData.append("what_exclude", excludeInput.value);
    const response = await fetch("/matches", { method: "POST", body: formData });
    if (!response.ok) {
      // FastAPI puts the error message in `detail` (e.g. the bad-PDF message).
      const errBody = await response.json().catch(() => null);
      throw new Error(errBody?.detail ?? `Server returned ${response.status}`);
    }
    const matches: Match[] = await response.json();

    if (matches.length === 0) {
      statusEl.textContent = "No jobs found. Try a different role, location, or fewer exclude words.";
      return;
    }
    statusEl.textContent = `${matches.length} jobs scored, best matches first.`;
    for (const m of matches) {
      const li = document.createElement("li");
      li.className = "card";
      li.innerHTML = `
        <div class="score">${m.score}</div>
        <div class="info">
          <h2>${m.title}</h2>
          <p class="meta">${m.company ?? ""} | ${m.location ?? ""}</p>
          <p class="explanation">${m.explanation}</p>
          ${m.url ? `<a href="${m.url}" target="_blank" rel="noopener">View listing</a>` : ""}
        </div>`;
      results.appendChild(li);
    }
  } catch (err) {
    statusEl.textContent = (err as Error).message;
  } finally {
    button.disabled = false;
  }
});
