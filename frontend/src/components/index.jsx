// Reusable presentational components shared by the transaction views.
// Keep Riskora visual language: low contrast, subtle borders, no motion.

import React from "react";

/* Empty state */
export function EmptyState({ title = "No transactions found", description = "Try changing your filters or search query." }) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon" aria-hidden="true">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M3 7h18M3 12h18M3 17h12" />
        </svg>
      </div>
      <p className="empty-state-title">{title}</p>
      <p className="empty-state-desc">{description}</p>
    </div>
  );
}

/* Error state */
export function ErrorState({ message = "Unable to load transactions.", onRetry }) {
  return (
    <div className="empty-state" role="alert">
      <div className="empty-state-icon" style={{ color: "var(--color-danger)" }} aria-hidden="true">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <p className="empty-state-title">{message}</p>
      {onRetry && (
        <button className="btn btn-outline retry-btn" onClick={onRetry}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: "6px" }}>
            <path d="M21 12a9 9 0 1 1-6.2-8.6" /><path d="M21 3v6h-6" />
          </svg>
          Retry
        </button>
      )}
    </div>
  );
}

/* Table skeleton */
export function TableSkeleton({ rows = 6, cols = 8 }) {
  return (
    <div className="table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {Array.from({ length: cols }).map((_, i) => (
              <th key={i}><span className="skeleton" /></th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, r) => (
            <tr key={r}>
              {Array.from({ length: cols }).map((_, c) => (
                <td key={c}><span className="skeleton" /></td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/* Detail-page skeleton */
export function DetailSkeleton() {
  return (
    <div className="detail-layout">
      {Array.from({ length: 3 }).map((_, s) => (
        <section key={s} className="card detail-block">
          <div className="skeleton skeleton-title" style={{ width: s === 0 ? "220px" : s === 1 ? "40%" : "55%" }} />
          <div className="detail-grid">
            {Array.from({ length: s === 2 ? 0 : 4 }).map((_, i) => (
              <div key={i} className="detail-field">
                <span className="skeleton skeleton-label" />
                <span className="skeleton skeleton-value" />
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}