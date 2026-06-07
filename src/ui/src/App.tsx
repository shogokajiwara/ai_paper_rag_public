import { useState } from "react";
import { useMachine } from "@xstate/react";
import ReactMarkdown from "react-markdown";
import { searchMachine } from "./machines/searchMachine";

export default function App() {
  const [query, setQuery] = useState("");

  // XState マシンを起動
  const [state, send] = useMachine(searchMachine);

  const { data, warning } = state.context;

  // 現在検索中かどうか
  const searching =
    state.matches("requestingJobId") ||
    state.matches("startingJob") ||
    state.matches("waitingResult");

  // -----------------------------
  // Search
  // -----------------------------
  function handleSearch() {
    console.log("handleSearch called. query =", query);
    if (!query.trim()) {
      console.log("→ query is empty. Sending WARNING");
      send({ type: "WARNING" });
      return;
    }
    console.log("→ sending SEARCH event:", { type: "SEARCH", query });
    send({ type: "SEARCH", query });
  }
  

  // -----------------------------
  // Cancel
  // -----------------------------
  function handleCancel() {
    send({
      type: "error",
      data: "Search canceled by user."
    });
  }

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: "2rem" }}>
      <h1>AI Paper RAG</h1>
      <p>A RAG system for exploring the latest AI research papers</p>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter the question or topic."
        style={{
          width: "700px",
          maxWidth: "100%",
          padding: "0.5rem",
          marginBottom: "1rem"
        }}
      />

      <div style={{ textAlign: "center" }}>
        {!searching ? (
          <button onClick={handleSearch}>Search</button>
        ) : (
          <button
            onClick={handleCancel}
            style={{ background: "red", color: "white" }}
          >
            Cancel
          </button>
        )}
      </div>

      {warning && (
        <div style={{ marginTop: "1rem", color: "red" }}>{warning}</div>
      )}

      {searching && (
        <div style={{ marginTop: "1rem", color: "#555" }}>
          Searching... (you can press Cancel)
        </div>
      )}

      {data && (
        <>
          <div style={{ textAlign: "left" }}>
            <h2>Answer</h2>
            <ReactMarkdown>{data.answer}</ReactMarkdown>
            <h2>Papers</h2>
          </div>

          {Array.isArray(data?.papers) && data.papers.length > 0 ? (
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginTop: "1rem"
              }}
            >
              <thead>
                <tr>
                  <th
                    style={{
                      textAlign: "left",
                      padding: "8px 4px",
                      borderBottom: "1px solid #ddd"
                    }}
                  >
                    title
                  </th>
                  <th
                    style={{
                      textAlign: "left",
                      padding: "8px 4px",
                      borderBottom: "1px solid #ddd"
                    }}
                  >
                    URL
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.papers.map((row, i) => (
                  <tr
                    key={i}
                    style={{
                      background: i % 2 === 0 ? "#fafafa" : "white"
                    }}
                  >
                    <td
                      style={{
                        padding: "8px 4px",
                        borderBottom: "1px solid #eee"
                      }}
                    >
                      {row.title}
                    </td>
                    <td
                      style={{
                        padding: "8px 4px",
                        borderBottom: "1px solid #eee"
                      }}
                    >
                      <a
                        href={row.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {row.url}
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No papers found.</p>
          )}
        </>
      )}
    </div>
  );
}
