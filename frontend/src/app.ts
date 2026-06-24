// Mirrors the Match model the backend returns from GET /matches.
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

button.addEventListener("click", async () => {
  // Disable the button and show progress while the (slow) scoring runs.
  button.disabled = true;
  statusEl.textContent = "Scoring jobs… this takes a few seconds.";
  results.innerHTML = "";

  try {
    const response = await fetch("/matches");
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const matches: Match[] = await response.json();

    statusEl.textContent = `${matches.length} jobs scored, best matches first.`;
    for (const m of matches) {
      const li = document.createElement("li");
      li.className = "card";
      li.innerHTML = `
        <div class="score">${m.score}</div>
        <div class="info">
          <h2>${m.title}</h2>
          <p class="meta">${m.company ?? ""} — ${m.location ?? ""}</p>
          <p class="explanation">${m.explanation}</p>
          ${m.url ? `<a href="${m.url}" target="_blank" rel="noopener">View listing</a>` : ""}
        </div>`;
      results.appendChild(li);
    }
  } catch (err) {
    statusEl.textContent = `Something went wrong: ${(err as Error).message}`;
  } finally {
    button.disabled = false;
  }
});
