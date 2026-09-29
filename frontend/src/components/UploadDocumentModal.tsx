"use client";

import React, { useState } from "react";
import { FileUp, Files, X, UploadCloud, CheckCircle, FileText, AlertCircle } from "lucide-react";

interface UploadDocumentModalProps {
  type: "employee" | "project";
  onClose: () => void;
  onSuccess: (msg: string) => void;
}

export default function UploadDocumentModal({
  type,
  onClose,
  onSuccess,
}: UploadDocumentModalProps) {
  const [entityName, setEntityName] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isIngested, setIsIngested] = useState(false);

  const title =
    type === "employee" ? "Upload Employee Resume/Document" : "Upload Project Document";
  const placeholder =
    type === "employee" ? "e.g. David or Alice" : "e.g. AI Customer Assistant";
  const targetDir =
    type === "employee" ? "data/graphrag/employees/" : "data/graphrag/projects/";

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      if (!entityName) {
        // extract name from filename (e.g., Alice_profile.txt -> Alice)
        const base = file.name.replace(/\.[^/.]+$/, "").replace(/_profile$/i, "").replace(/_/g, " ");
        setEntityName(base);
      }
    }
  };

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !entityName.trim()) return;

    setIsIngested(true);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {type === "employee" ? (
              <FileUp size={18} color="var(--purple-primary)" />
            ) : (
              <Files size={18} color="var(--purple-primary)" />
            )}
            <span className="modal-title">{title}</span>
          </div>
          <button
            onClick={onClose}
            style={{ background: "transparent", border: "none", cursor: "pointer", color: "#64748b" }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <div className="info-banner">
            <strong>GraphRAG Pipeline Context:</strong> Uploaded documents ({type === "employee" ? "resumes, CVs, profiles" : "requirements, tech specs, scopes"}) are chunked into sentence embeddings and stored in Neo4j <code>:Document</code> nodes via <code>graphrag_ingest.py</code>.
          </div>

          {isIngested ? (
            <div style={{ textAlign: "center", padding: "24px 12px" }}>
              <div
                style={{
                  width: "48px",
                  height: "48px",
                  background: "var(--green-light)",
                  border: "2px solid var(--border-dark)",
                  borderRadius: "50%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 14px",
                  color: "var(--green-primary)",
                }}
              >
                <CheckCircle size={24} />
              </div>
              <h3 style={{ fontSize: "16px", fontWeight: 800 }}>Document Processed</h3>
              <p style={{ fontSize: "12.5px", color: "var(--text-muted)", marginTop: "6px" }}>
                <strong>{selectedFile?.name}</strong> associated with {type} <strong>{entityName}</strong>. Ready for GraphRAG semantic chunking.
              </p>
              <button
                className="nb-btn nb-btn-primary"
                style={{ marginTop: "18px" }}
                onClick={onClose}
              >
                Done
              </button>
            </div>
          ) : (
            <form onSubmit={handleUpload}>
              <div className="form-group">
                <label className="form-label">
                  Associated {type === "employee" ? "Employee Name" : "Project Name"} *
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder={placeholder}
                  value={entityName}
                  onChange={(e) => setEntityName(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Document File (.txt, .pdf) *</label>
                <div
                  style={{
                    border: "2px dashed var(--border-dark)",
                    borderRadius: "8px",
                    padding: "24px",
                    textAlign: "center",
                    background: "#fbfbfe",
                    cursor: "pointer",
                    position: "relative",
                  }}
                >
                  <input
                    type="file"
                    accept=".txt,.pdf"
                    onChange={handleFileChange}
                    style={{
                      position: "absolute",
                      inset: 0,
                      opacity: 0,
                      cursor: "pointer",
                      width: "100%",
                      height: "100%",
                    }}
                    required={!selectedFile}
                  />
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}>
                    <UploadCloud size={32} color="var(--purple-primary)" />
                    {selectedFile ? (
                      <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <FileText size={16} color="#000000" />
                        <span style={{ fontWeight: 700, fontSize: "13px", color: "#000000" }}>
                          {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                    ) : (
                      <>
                        <span style={{ fontWeight: 700, fontSize: "13px", color: "#000000" }}>
                          Choose a file or drag & drop here
                        </span>
                        <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                          Supported formats: TXT, PDF (Max 15MB)
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div style={{ fontSize: "11px", color: "var(--text-muted)", marginBottom: "16px" }}>
                Target Directory: <code>{targetDir}</code>
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                <button type="button" className="nb-btn" onClick={onClose}>
                  Cancel
                </button>
                <button
                  type="submit"
                  className="nb-btn nb-btn-primary"
                  disabled={!selectedFile || !entityName.trim()}
                >
                  <UploadCloud size={14} />
                  <span>Ingest Document</span>
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
