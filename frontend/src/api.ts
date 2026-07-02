const TOKEN_KEY = "kb_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (!(options.body instanceof FormData) && options.body) {
    headers.set("Content-Type", "application/json");
  }

  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail.detail || "Ошибка запроса");
  }
  return res.json();
}

export interface SourceRef {
  document_id: string;
  document_title: string;
  section_label: string;
  chunk_id: string;
  excerpt: string;
}

export interface SearchResponse {
  answer: string;
  grounded: boolean;
  detected_language: string;
  sources: SourceRef[];
}

export function search(query: string): Promise<SearchResponse> {
  return request("/api/search", { method: "POST", body: JSON.stringify({ query }) });
}

export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch("/api/auth/login", { method: "POST", body });
  if (!res.ok) throw new Error("Неверный email или пароль");
  const data = await res.json();
  setToken(data.access_token);
  return data.access_token;
}

export interface DocumentOut {
  id: string;
  title: string;
  source_filename: string;
  language: string;
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export function listDocuments(): Promise<DocumentOut[]> {
  return request("/api/documents");
}

export async function uploadDocument(file: File, title: string): Promise<DocumentOut> {
  const formData = new FormData();
  formData.append("file", file);
  const params = new URLSearchParams({ title });
  return request(`/api/documents?${params.toString()}`, { method: "POST", body: formData });
}

export function archiveDocument(id: string): Promise<DocumentOut> {
  return request(`/api/documents/${id}/archive`, { method: "PATCH" });
}
