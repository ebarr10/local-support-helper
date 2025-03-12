"use client";

import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState("");
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse("Loading...");
    setProcessing(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/ask", {
        question,
      });
      setResponse(res.data.response);
    } catch (error) {
      setResponse("Error fetching response.");
      console.error(error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="text-2xl font-bold mb-4">AI Support Assistant</h1>
      <form onSubmit={handleSubmit} className="w-full max-w-md">
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="w-full p-2 border rounded-md mb-2"
        />
        <button
          type="submit"
          disabled={processing}
          className="w-full p-2 bg-blue-500 text-white rounded-md"
        >
          Ask
        </button>
      </form>
      {response ? (
        <div className="mt-6 p-4 border rounded-md w-full max-w-md">
          <ReactMarkdown>{response}</ReactMarkdown>
        </div>
      ) : (
        <></>
      )}
    </div>
  );
}
