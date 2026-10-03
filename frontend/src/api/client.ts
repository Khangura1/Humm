const PRODUCTION_URL = "https://humm-h9dc.onrender.com"
const API_URL = import.meta.env.DEV ? "http://localhost:8000" : PRODUCTION_URL


export async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

