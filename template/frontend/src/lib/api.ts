const API_URL = import.meta.env.VITE_API_URL || "";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options?.headers,
  };

  // Modal auth headers - required for all API calls (proxy auth is always enabled)
  const modalKey = import.meta.env.VITE_MODAL_KEY;
  const modalSecret = import.meta.env.VITE_MODAL_SECRET;

  if (modalKey && modalSecret) {
    headers["Modal-Key"] = modalKey;
    headers["Modal-Secret"] = modalSecret;
  } else if (API_URL) {
    console.error(
      "Missing VITE_MODAL_KEY and VITE_MODAL_SECRET in .env.local - API calls will fail with 401. " +
        "Create a token at https://modal.com/settings/proxy-auth-tokens"
    );
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error(
        "API authentication failed. Check VITE_MODAL_KEY and VITE_MODAL_SECRET in .env.local"
      );
    }
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}
