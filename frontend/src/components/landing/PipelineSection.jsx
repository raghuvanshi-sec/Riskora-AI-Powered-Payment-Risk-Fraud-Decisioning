export default function PipelineSection() {
  const stages = [
    {
      num: '01',
      title: 'Transaction Signals',
      desc: 'Raw payment events observed',
    },
    {
      num: '02',
      title: 'Merchant Baseline',
      desc: 'Normal activity patterns established',
    },
    {
      num: '03',
      title: 'Spike Detection',
      desc: 'Abnormal fraud activity identified',
    },
    {
      num: '04',
      title: 'Exposure Estimation',
      desc: 'Financial impact quantified',
    },
    {
      num: '05',
      title: 'Defensive Action',
      desc: 'Bounded recommendations generated',
    },
  ];

  return (
    <section className="ld-section" id="pipeline">
      <div className="ld-container">
        <div className="ld-section-head">
          <div className="ld-eyebrow">How It Works</div>
          <h2 className="ld-h2">Systematic fraud risk operations</h2>
          <p className="ld-lede">
            A structured approach from transaction data to explainable defensive recommendations.
          </p>
        </div>

        <div className="ld-pipeline">
          {stages.map((stage) => (
            <div key={stage.num} className="ld-pipeline__stage">
              <div className="ld-pipeline__num">{stage.num}</div>
              <h3 className="ld-pipeline__title">{stage.title}</h3>
              <p className="ld-pipeline__desc">{stage.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
