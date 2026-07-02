import { useEffect, useState } from "react";
import { archiveDocument, listDocuments, uploadDocument, type DocumentOut } from "../api";

export default function AdminPage() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  const refresh = () => {
    listDocuments()
      .then(setDocuments)
      .catch((e) => setError(e.message));
  };

  useEffect(refresh, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file, title || file.name);
      setFile(null);
      setTitle("");
      refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="page">
      <h1>Управление документами</h1>
      <form className="upload-form" onSubmit={handleUpload}>
        <input
          type="text"
          placeholder="Название документа"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button type="submit" disabled={!file || uploading}>
          {uploading ? "Загрузка…" : "Загрузить"}
        </button>
      </form>
      {error && <p className="error">{error}</p>}

      <table className="doc-table">
        <thead>
          <tr>
            <th>Название</th>
            <th>Файл</th>
            <th>Статус</th>
            <th>Версия</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>{doc.title}</td>
              <td>{doc.source_filename}</td>
              <td>{doc.status}</td>
              <td>{doc.version}</td>
              <td>
                {doc.status === "active" && (
                  <button
                    onClick={async () => {
                      await archiveDocument(doc.id);
                      refresh();
                    }}
                  >
                    Архивировать
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
