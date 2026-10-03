import { useEffect, useState } from "react";
import { request } from "./api/client";

type Status = "checking" | "healthy" | "unhealthy";

type HealthResponse = {
  status: string;
};

const MESSAGES: Record<Status, string> = 
{
  checking: "Checking the API...",
  healthy: "API is running",
  unhealthy: "API is unreachable",
};

export default function App() 
{
  const [status, setStatus] = useState<Status>("checking");

  useEffect(() => 
  {
    request<HealthResponse>("/api/health")
      .then(() => setStatus("healthy"))
      .catch(() => setStatus("unhealthy"));
  }, []);

  return (
    <main>
      <h1>Humm</h1>
      <p>{MESSAGES[status]}</p>
    </main>
  );
}

