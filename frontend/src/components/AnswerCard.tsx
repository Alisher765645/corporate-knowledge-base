import type { SearchResponse } from "../api";

export default function AnswerCard({ result }: { result: SearchResponse }) {
  return (
    <div className="answer-card">
      <p className="answer-text">{result.answer}</p>
      {result.sources.length > 0 && (
        <div className="sources">
          <h4>Источники</h4>
          <ul>
            {result.sources.map((s) => (
              <li key={s.chunk_id}>
                <strong>{s.document_title}</strong>
                {s.section_label && <span> · раздел {s.section_label}</span>}
                <p className="excerpt">{s.excerpt}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
