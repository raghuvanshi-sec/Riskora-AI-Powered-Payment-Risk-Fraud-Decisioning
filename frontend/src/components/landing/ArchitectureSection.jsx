export default function ArchitectureSection() {
  const layers = [
    {
      title: 'Data Ingestion',
      nodes: ['Transactions', 'Event Streams', 'Batch Data'],
    },
    {
      title: 'Risk Processing',
      nodes: ['Feature Extraction', 'Rule Engine', 'XGBoost Model', 'SHAP Attribution'],
    },
    {
      title: 'Decision Layer',
      nodes: ['Risk Classification', 'Threshold Policy', 'Defensive Actions'],
    },
    {
      title: 'Operations',
      nodes: ['Case Queue', 'Analyst Review', 'Audit Trail', 'Reporting'],
    },
  ];

  return (
    <section className="ld-section" id="architecture">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">Architecture</div>
          <h2 className="ld-h2">System overview</h2>
          <p className="ld-lede">
            From raw transaction ingestion to explainable defensive action.
          </p>
        </div>

        <div className="ld-arch">
          {layers.map((layer, i) => (
            <div key={i} className="ld-arch__layer">
              <div className="ld-arch__layer-title">{layer.title}</div>
              <div className="ld-arch__nodes">
                {layer.nodes.map((node, j) => (
                  <div key={j} className={`ld-arch__node ${j === 0 || j === layer.nodes.length - 1 ? 'ld-arch__node--accent' : ''}`}>
                    {node}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
