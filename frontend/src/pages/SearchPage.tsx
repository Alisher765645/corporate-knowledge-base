import { useState } from "react";
import SearchBox from "../components/SearchBox";
import AnswerCard from "../components/AnswerCard";
import { search, type SearchResponse } from "../api";

export default function SearchPage() {
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await search(query);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка поиска");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page center-page">
      <h1>База знаний по нормативным документам</h1>
      <SearchBox onSearch={handleSearch} loading={loading} />
      {error && <p className="error">{error}</p>}
      {result && <AnswerCard result={result} />}
    </div>
  );
}
