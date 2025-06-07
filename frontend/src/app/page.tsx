'use client';

import { useState, useRef, useEffect } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [clonedHtml, setClonedHtml] = useState("");
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<"preview" | "code">("preview");
  const previewRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (clonedHtml && previewRef.current) {
      previewRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [clonedHtml]);

  const handleClone = async () => {
    if (!url) return;
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/clone", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail}`);
        setLoading(false);
        return;
      }

      const data = await response.json();
      setClonedHtml(data.cloned_html);
    } catch (err) {
      alert("Something went wrong while cloning.");
    }

    setLoading(false);
  };

  return (
    <main
      style={{
        position: "relative",
        zIndex: 1,
        minHeight: "100vh",
        fontFamily: "Inter, sans-serif",
        color: "white",
        overflow: "hidden",
        backgroundColor: "#0F172A",
        backgroundImage: "radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px)",
        backgroundSize: "30px 30px",
      }}
    >
      {/* Purple Blob */}
      <div
        style={{
          position: "absolute",
          top: "-200px",
          left: "-200px",
          width: "500px",
          height: "500px",
          background: "radial-gradient(circle at center, #7c3aed 0%, #0F172A 90%)",
          opacity: 0.4,
          filter: "blur(120px)",
          animation: "blobAnimation 15s infinite ease-in-out",
          zIndex: -1,
        }}
      />

      {/* Hero Input Section */}
      <div
        style={{
          display: "flex",
          minHeight: "100vh",
          alignItems: "center",
          justifyContent: "flex-start",
          paddingLeft: "10%",
          paddingRight: "10%",
          position: "relative",
          zIndex: 2,
        }}
      >
        <div style={{ maxWidth: "600px" }}>
          <h1 style={{ fontSize: "3rem", fontWeight: 800, lineHeight: 1.2, color: "white" }}>
            Clone any website<br /><span style={{ color: "#a855f7" }}>in seconds</span>
          </h1>
          <p style={{ marginTop: "20px", fontSize: "1.1rem", color: "#cbd5e1", maxWidth: "550px" }}>
            Enter any URL and get a perfect clone with just one click. Fast, reliable, and incredibly simple.
          </p>

          <div
            style={{
              marginTop: "40px",
              display: "flex",
              alignItems: "center",
              background: "linear-gradient(135deg, #1e293b, #334155)",
              padding: "4px",
              borderRadius: "14px",
              maxWidth: "560px",
              width: "100%",
              position: "relative",
              overflow: "hidden",
              boxShadow: "0 8px 24px rgba(0, 0, 0, 0.3)",
            }}
          >
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                background: "linear-gradient(to right, #0f172a, #1e293b)",
                padding: "6px",
                borderRadius: "12px",
                transition: "transform 0.2s ease",
              }}
            >
              <input
                type="text"
                placeholder="Enter website URL (e.g., https://example.com)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                style={{
                  flex: 1,
                  padding: "14px 18px",
                  fontSize: "1rem",
                  fontFamily: "Inter, sans-serif",
                  color: "white",
                  background: "transparent",
                  border: "none",
                  outline: "none",
                }}
              />
            </div>

            <button
              onClick={handleClone}
              style={{
                marginLeft: "8px",
                padding: "19px 24px",
                fontSize: "15px",
                fontWeight: "600",
                border: "none",
                borderRadius: "10px",
                background: "linear-gradient(270deg, #8b5cf6, #4f46e5, #9333ea)",
                backgroundSize: "600% 600%",
                color: "white",
                cursor: "pointer",
                animation: "clonePulse 4s ease infinite",
              }}
            >
              {loading ? "Cloning..." : "Clone Now"}
            </button>
          </div>
        </div>
      </div>

      {/* Cloned Preview or Code View */}
      {clonedHtml && (
        <div
          ref={previewRef}
          style={{
            marginTop: "40px",
            width: "100%",
            minHeight: "100vh",
            background: "#1e293b",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px" }}>
            <h2 style={{ color: "#fff" }}>Cloned Result</h2>
            <button
              onClick={() => setViewMode(viewMode === "preview" ? "code" : "preview")}
              style={{
                padding: "8px 16px",
                fontSize: "14px",
                backgroundColor: "#334155",
                color: "#fff",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
              }}
            >
              {viewMode === "preview" ? "View Code" : "View Preview"}
            </button>
          </div>

          {viewMode === "preview" ? (
            <iframe
              srcDoc={clonedHtml}
              style={{
                width: "100%",
                height: "calc(100vh - 80px)",
                border: "none",
                backgroundColor: "#fff",
              }}
            />
          ) : (
            <textarea
              readOnly
              value={clonedHtml}
              style={{
                width: "100%",
                height: "calc(100vh - 80px)",
                padding: "16px",
                fontFamily: "monospace",
                fontSize: "14px",
                backgroundColor: "#0f172a",
                color: "#e2e8f0",
                border: "none",
                resize: "none",
              }}
            />
          )}
        </div>
      )}

      {/* Keyframe Animations */}
      <style jsx>{`
        @keyframes blobAnimation {
          0% { transform: scale(1); }
          50% { transform: scale(1.15); }
          100% { transform: scale(1); }
        }

        @keyframes clonePulse {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }

        @keyframes floatPage {
          0% { transform: translateY(0px) rotate(2deg); }
          50% { transform: translateY(-10px) rotate(2deg); }
          100% { transform: translateY(0px) rotate(2deg); }
        }
      `}</style>
    </main>
  );
}
