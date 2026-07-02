import { useState } from "react";

const MAX_CHARS = 5000;

interface Props {
  onSearch: (query: string) => void;
  loading: boolean;
}

export default function SearchBox({ onSearch, loading }: Props) {
  const [value, setValue] = useState("");

  const submit = () => {
    const trimmed = value.trim();
    if (trimmed) onSearch(trimmed);
  };

  return (
    <div className="search-box">
      <textarea
        className="search-input"
        placeholder="Задайте вопрос или введите ключевые слова…"
        value={value}
        maxLength={MAX_CHARS}
        rows={3}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
      />
      <div className="search-box-footer">
        <span className={value.length > MAX_CHARS * 0.9 ? "char-count warn" : "char-count"}>
          {value.length} / {MAX_CHARS}
        </span>
        <button onClick={submit} disabled={loading || !value.trim()}>
          {loading ? "Поиск…" : "Найти"}
        </button>
      </div>
    </div>
  );
}
