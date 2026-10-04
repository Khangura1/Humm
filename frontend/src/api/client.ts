const PRODUCTION_URL = "https://humm-h9dc.onrender.com"
const API_URL = import.meta.env.DEV ? "http://localhost:8000" : PRODUCTION_URL


async function readError(response: Response, path: string): Promise<Error> {
  // FastAPI sends errors as {"detail": "..."}
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      return new Error(body.detail);
    }
  } catch {
    // the body wasn't JSON, fall through to the generic message
  }
  return new Error(`Request to ${path} failed with status ${response.status}`);
}

export async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    throw await readError(response, path);
  }

  return (await response.json()) as T;
}

export async function postForm<T>(path: string, form: FormData): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { method: "POST", body: form });

  if (!response.ok) {
    throw await readError(response, path);
  }

  return (await response.json()) as T;
}
