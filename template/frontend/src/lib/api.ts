const API_URL = import.meta.env.VITE_API_URL || "";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options?.headers,
  };

  // Add Modal auth headers if configured
  const modalKey = import.meta.env.VITE_MODAL_KEY;
  const modalSecret = import.meta.env.VITE_MODAL_SECRET;
  if (modalKey && modalSecret) {
    headers["Modal-Key"] = modalKey;
    headers["Modal-Secret"] = modalSecret;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
