import React, { useState, useMemo } from "react";
import { useStreamContext } from "@langchain/langgraph-sdk/react-ui";

// Inline styles for consistent rendering
const styles = {
  container: {
    borderRadius: "8px",
    border: "2px solid #86efac",
    backgroundColor: "#ffffff",
    padding: "20px",
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
  },
  successHeader: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    color: "#15803d",
    marginBottom: "16px",
    fontSize: "14px",
    fontWeight: "600",
  },
  fileInfoSection: {
    display: "flex",
    flexWrap: "wrap" as const,
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: "16px",
    marginBottom: "16px",
  },
  iconBox: {
    borderRadius: "8px",
    backgroundColor: "#dcfce7",
    padding: "8px",
  },
  fileName: {
    fontSize: "16px",
    fontWeight: "600",
    color: "#111827",
    marginBottom: "4px",
  },
  fileInfo: {
    fontSize: "14px",
    color: "#6b7280",
  },
  button: {
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    borderRadius: "6px",
    backgroundColor: "#2563eb",
    color: "#ffffff",
    padding: "8px 16px",
    fontSize: "14px",
    fontWeight: "500",
    border: "none",
    cursor: "pointer",
    boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    transition: "background-color 0.15s",
    height: "36px",
    maxWidth: "fit-content",
  },
  secondaryButton: {
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    borderRadius: "6px",
    backgroundColor: "#ffffff",
    color: "#374151",
    padding: "8px 16px",
    fontSize: "14px",
    fontWeight: "500",
    border: "1px solid #d1d5db",
    cursor: "pointer",
    boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    transition: "background-color 0.15s",
    height: "36px",
    maxWidth: "fit-content",
  },
  table: {
    minWidth: "100%",
    borderCollapse: "collapse" as const,
  },
  th: {
    padding: "12px 16px",
    textAlign: "left" as const,
    fontSize: "12px",
    fontWeight: "600",
    textTransform: "uppercase" as const,
    letterSpacing: "0.05em",
    color: "#374151",
    backgroundColor: "#f9fafb",
    borderBottom: "1px solid #e5e7eb",
  },
  td: {
    padding: "12px 16px",
    fontSize: "14px",
    color: "#111827",
    whiteSpace: "nowrap" as const,
    borderBottom: "1px solid #e5e7eb",
  },
  pendingContainer: {
    borderRadius: "8px",
    border: "1px solid #93c5fd",
    backgroundColor: "#eff6ff",
    padding: "16px",
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
  },
  errorContainer: {
    borderRadius: "8px",
    border: "1px solid #fca5a5",
    backgroundColor: "#fef2f2",
    padding: "16px",
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
  },
};

// Icon Components
const DownloadIcon = () => (
  <svg style={{width: "16px", height: "16px", minWidth: "16px", minHeight: "16px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
  </svg>
);

const CheckIcon = () => (
  <svg style={{width: "20px", height: "20px", minWidth: "20px", minHeight: "20px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const AlertIcon = () => (
  <svg style={{width: "20px", height: "20px", minWidth: "20px", minHeight: "20px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const SpinnerIcon = () => (
  <svg style={{width: "20px", height: "20px", minWidth: "20px", minHeight: "20px", flexShrink: 0, animation: "spin 1s linear infinite"}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle style={{opacity: 0.25}} cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path style={{opacity: 0.75}} fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
);

const TableIcon = () => (
  <svg style={{width: "20px", height: "20px", minWidth: "20px", minHeight: "20px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
  </svg>
);

const FileTextIcon = () => (
  <svg style={{width: "20px", height: "20px", minWidth: "20px", minHeight: "20px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
);

const ChevronDownIcon = () => (
  <svg style={{width: "16px", height: "16px", minWidth: "16px", minHeight: "16px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

const ChevronUpIcon = () => (
  <svg style={{width: "16px", height: "16px", minWidth: "16px", minHeight: "16px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
  </svg>
);

const EyeIcon = () => (
  <svg style={{width: "16px", height: "16px", minWidth: "16px", minHeight: "16px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
  </svg>
);

const EyeOffIcon = () => (
  <svg style={{width: "16px", height: "16px", minWidth: "16px", minHeight: "16px", flexShrink: 0}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
  </svg>
);

// CSV Preview Component
const CSVPreview = () => {
  const context = useStreamContext();
  const [showFullTable, setShowFullTable] = useState(false);
  
  const meta = context?.meta as any;
  const result = meta?.result;
  const status = meta?.status || "pending";

  const toolResult = useMemo(() => {
    if (!result) return null;
    try {
      return JSON.parse(result);
    } catch (error) {
      return null;
    }
  }, [result]);

  const csvData = useMemo(() => {
    if (!toolResult?.data) return { headers: [], rows: [] };
    try {
      const decoded = atob(toolResult.data);
      const lines = decoded.split("\n").filter(line => line.trim());
      if (lines.length === 0) return { headers: [], rows: [] };

      const headers = lines[0].split(",").map(h => h.trim());
      const rows = lines.slice(1).map(line => 
        line.split(",").map(cell => cell.trim())
      );

      return { headers, rows };
    } catch (error) {
      return { headers: [], rows: [] };
    }
  }, [toolResult]);

  const handleDownload = () => {
    if (!toolResult?.data) return;
    try {
      const decoded = atob(toolResult.data);
      const blob = new Blob([decoded], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = toolResult.filename || "report.csv";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("[CSVPreview] Failed to download CSV:", error);
    }
  };

  if (status === "pending") {
    return (
      <div style={styles.pendingContainer}>
        <div style={{display: "flex", alignItems: "center", gap: "12px", color: "#1d4ed8"}}>
          <SpinnerIcon />
          <span style={{fontSize: "14px", fontWeight: "500"}}>Generating CSV report...</span>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div style={styles.errorContainer}>
        <div style={{display: "flex", alignItems: "center", gap: "12px", color: "#b91c1c"}}>
          <AlertIcon />
          <span style={{fontSize: "14px", fontWeight: "500"}}>Failed to generate CSV report</span>
        </div>
      </div>
    );
  }

  if (!toolResult) {
    return (
      <div style={{...styles.pendingContainer, borderColor: "#fcd34d", backgroundColor: "#fef3c7"}}>
        <div style={{fontSize: "14px", color: "#92400e"}}>Waiting for CSV data...</div>
      </div>
    );
  }

  const displayRows = showFullTable ? csvData.rows : csvData.rows.slice(0, 5);
  const hasMoreRows = csvData.rows.length > 5;

  return (
    <div style={styles.container}>
      <div style={styles.successHeader}>
        <CheckIcon />
        <span>CSV Report Generated</span>
      </div>

      <div style={styles.fileInfoSection}>
        <div style={{display: "flex", alignItems: "flex-start", gap: "12px"}}>
          <div style={styles.iconBox}>
            <TableIcon />
          </div>
          <div>
            <h3 style={styles.fileName}>{toolResult.filename}</h3>
            <p style={styles.fileInfo}>
              {toolResult.rows || csvData.rows.length} rows • {csvData.headers.length} columns
            </p>
          </div>
        </div>
        <button 
          onClick={handleDownload}
          style={styles.button}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#1d4ed8"}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#2563eb"}
        >
          <DownloadIcon />
          Download CSV
        </button>
      </div>

      {csvData.headers.length > 0 && (
        <div style={{marginTop: "12px"}}>
          <div style={{overflow: "hidden", borderRadius: "8px", border: "1px solid #e5e7eb"}}>
            <div style={{overflowX: "auto"}}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    {csvData.headers.map((header, idx) => (
                      <th key={idx} style={styles.th}>{header}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {displayRows.map((row, rowIdx) => (
                    <tr key={rowIdx}>
                      {row.map((cell, cellIdx) => (
                        <td key={cellIdx} style={styles.td}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          {hasMoreRows && (
            <div style={{display: "flex", justifyContent: "center", marginTop: "12px"}}>
              <button
                onClick={() => setShowFullTable(!showFullTable)}
                style={styles.secondaryButton}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#f9fafb"}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#ffffff"}
              >
                {showFullTable ? (
                  <>
                    <ChevronUpIcon />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDownIcon />
                    Show all {csvData.rows.length} rows
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// PDF Preview Component
const PDFPreview = () => {
  const context = useStreamContext();
  const [showPreview, setShowPreview] = useState(false);
  
  const meta = context?.meta as any;
  const result = meta?.result;
  const status = meta?.status || "pending";

  const toolResult = useMemo(() => {
    if (!result) return null;
    try {
      return JSON.parse(result);
    } catch (error) {
      return null;
    }
  }, [result]);

  const handleDownload = () => {
    if (!toolResult?.data) return;
    try {
      const decoded = atob(toolResult.data);
      const bytes = new Uint8Array(decoded.length);
      for (let i = 0; i < decoded.length; i++) {
        bytes[i] = decoded.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: "application/pdf" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = toolResult.filename || "report.pdf";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("[PDFPreview] Failed to download PDF:", error);
    }
  };

  const previewUrl = useMemo(() => {
    if (!toolResult?.data) return null;
    try {
      const decoded = atob(toolResult.data);
      const bytes = new Uint8Array(decoded.length);
      for (let i = 0; i < decoded.length; i++) {
        bytes[i] = decoded.charCodeAt(i);
      }
      const blob = new Blob([bytes], { type: "application/pdf" });
      return URL.createObjectURL(blob);
    } catch (error) {
      return null;
    }
  }, [toolResult]);

  if (status === "pending") {
    return (
      <div style={styles.pendingContainer}>
        <div style={{display: "flex", alignItems: "center", gap: "12px", color: "#1d4ed8"}}>
          <SpinnerIcon />
          <span style={{fontSize: "14px", fontWeight: "500"}}>Generating PDF report...</span>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div style={styles.errorContainer}>
        <div style={{display: "flex", alignItems: "center", gap: "12px", color: "#b91c1c"}}>
          <AlertIcon />
          <span style={{fontSize: "14px", fontWeight: "500"}}>Failed to generate PDF report</span>
        </div>
      </div>
    );
  }

  if (!toolResult) {
    return (
      <div style={{...styles.pendingContainer, borderColor: "#fcd34d", backgroundColor: "#fef3c7"}}>
        <div style={{fontSize: "14px", color: "#92400e"}}>Waiting for PDF data...</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.successHeader}>
        <CheckIcon />
        <span>PDF Report Generated</span>
      </div>

      <div style={styles.fileInfoSection}>
        <div style={{display: "flex", alignItems: "flex-start", gap: "12px"}}>
          <div style={{...styles.iconBox, backgroundColor: "#fee2e2"}}>
            <FileTextIcon />
          </div>
          <div>
            <h3 style={styles.fileName}>{toolResult.filename}</h3>
            <p style={styles.fileInfo}>
              {toolResult.rows && `${toolResult.rows} rows`}
              {toolResult.pages && ` • ${toolResult.pages} page${toolResult.pages > 1 ? "s" : ""}`}
            </p>
          </div>
        </div>
        <div style={{display: "flex", gap: "8px"}}>
          <button
            onClick={() => setShowPreview(!showPreview)}
            style={styles.secondaryButton}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#f9fafb"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#ffffff"}
          >
            {showPreview ? (
              <>
                <EyeOffIcon />
                Hide Preview
              </>
            ) : (
              <>
                <EyeIcon />
                Show Preview
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            style={styles.button}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#1d4ed8"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#2563eb"}
          >
            <DownloadIcon />
            Download PDF
          </button>
        </div>
      </div>

      {showPreview && previewUrl && (
        <div style={{marginTop: "16px", overflow: "hidden", borderRadius: "8px", border: "1px solid #e5e7eb"}}>
          <iframe
            src={previewUrl}
            style={{width: "100%", height: "600px", backgroundColor: "#f9fafb", border: "none"}}
            title="PDF Preview"
          />
        </div>
      )}

      {showPreview && !previewUrl && (
        <div style={{...styles.errorContainer, marginTop: "16px"}}>
          <div style={{display: "flex", alignItems: "flex-start", gap: "12px", fontSize: "14px", color: "#b91c1c"}}>
            <AlertIcon />
            <div>
              <p style={{fontWeight: "500", margin: 0}}>Failed to load PDF preview</p>
              <p style={{marginTop: "4px", color: "#dc2626"}}>
                Please try downloading the file instead.
              </p>
            </div>
          </div>
        </div>
      )}
      
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default {
  csv_preview: CSVPreview,
  pdf_preview: PDFPreview,
};
