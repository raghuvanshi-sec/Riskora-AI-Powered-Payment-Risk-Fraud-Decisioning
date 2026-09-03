export default function PipelineSection() {
  const stages = [
    {
      num: '1',
      label: 'Transaction',
      desc: 'Payment events observed',
    },
    {
      num: '2',
      label: 'Feature Extract',
      desc: 'Signals processed',
    },
    {
      num: '3',
      label: 'Rule + XGBoost',
      desc: 'Hybrid scoring',
    },
    {
      num: '4',
      label: 'Risk Score',
      desc: '0-100 scale',
    },
    {
      num: '5',
      label: 'Classification',
      desc: 'LOW/MED/HIGH',
    },
    {
      num: '6',
      label: 'ALLOW/REVIEW',
      desc: 'Decision actioned',
    },
    {
      num: '7',
      label: 'Audit Trail',
      desc: 'Logged & tracked',
    },
  ];

  return (
    <section className="ld-section ld-section--alt" id="pipeline">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">How It Works</div>
          <h2 className="ld-h2">Enterprise risk engine architecture</h2>
          <p className="ld-lede">
            From transaction evaluation to explainable decisions — all within bounded policy controls.
          </p>
        </div>

        <div className="ld-pipeline">
          {stages.map((stage) => (
            <div key={stage.num} className="ld-pipeline__stage">
              <div className="ld-pipeline__num">{stage.num}</div>
              <div className="ld-pipeline__label">{stage.label}</div>
              <div className="ld-pipeline__desc">{stage.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
