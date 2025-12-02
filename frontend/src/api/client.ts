export async function fetchRepo(repoUrl: string): Promise<string> {
  const res = await fetch("http://127.0.0.1:8000/api/fetch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });

  if (!res.ok) throw new Error(await res.text());
  return (await res.json()).local_path;
}

export async function analyzeRepo(path: string) {
  const res = await fetch("http://127.0.0.1:8000/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ local_path: path }),
  });

  if (!res.ok) throw new Error(await res.text());
  return (await res.json()).analysis_report;
}
