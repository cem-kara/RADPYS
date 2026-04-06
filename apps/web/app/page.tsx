import { getHealth } from "../lib/api-client";

export default async function Home() {
  let healthSummary: string;

  try {
    const health = await getHealth();
    healthSummary = `${health.service} is ${health.status}`;
  } catch (error) {
    healthSummary = "API is not reachable yet";
  }

  return (
    <main>
      <div className="container hero">
        <span className="badge">REPYS Next</span>
        <h1>Welcome to the new REPYS platform.</h1>
        <p className="meta">
          This page is wired to the API health endpoint to validate
          connectivity.
        </p>
        <div className="card">
          <strong>API health</strong>
          <p>{healthSummary}</p>
        </div>
      </div>
    </main>
  );
}
