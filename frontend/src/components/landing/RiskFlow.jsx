import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

function SignalPulse({ delay }) {
  return (
    <motion.div
      style={{
        position: 'absolute',
        left: '50%',
        top: '50%',
        width: 12,
        height: 12,
        borderRadius: '50%',
        background: '#8b5cf6',
      }}
      animate={{
        x: '-50%',
        y: '-50%',
        opacity: [0, 0.8, 0],
        scale: [0.3, 1.5, 2],
      }}
      transition={{
        duration: 1.8,
        delay,
        repeat: Infinity,
        ease: 'easeOut',
      }}
    />
  );
}

function ExposureMeter({ value }) {
  return (
    <motion.div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-end',
        gap: 2,
      }}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', color: '#64748b' }}>EXPOSURE</span>
      <span style={{ fontSize: 24, fontWeight: 800, fontFamily: 'var(--font-mono, monospace)', color: '#ef4444', letterSpacing: '-0.02em' }}>{value}</span>
    </motion.div>
  );
}

function ActionCard({ action, active }) {
  return (
    <motion.div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 4,
        padding: '6px 10px',
        background: active ? 'linear-gradient(135deg, #22c55e, #16a34a)' : 'rgba(15, 23, 42, 0.9)',
        border: `1px solid ${active ? '#22c55e' : 'rgba(148, 163, 184, 0.2)'}`,
        borderRadius: 6,
        boxShadow: active ? '0 4px 12px rgba(34, 197, 94, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.3)',
      }}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <span style={{ fontSize: 10, color: active ? 'white' : '#22c55e' }}>✓</span>
      <span style={{ fontSize: 9, fontWeight: 600, color: active ? 'white' : '#94a3b8', letterSpacing: '0.05em' }}>{action}</span>
    </motion.div>
  );
}

export default function RiskFlow() {
  const [spikeActive, setSpikeActive] = useState(false);
  const [exposureValue, setExposureValue] = useState('$12k');
  const [currentAction, setCurrentAction] = useState('MONITOR');
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 560, height: 520 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth || 560,
          height: containerRef.current.clientHeight || 520,
        });
      }
    };

    updateDimensions();
    const ro = new ResizeObserver(updateDimensions);
    if (containerRef.current) ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const cycleSpike = () => {
      setTimeout(() => {
        setSpikeActive(true);
        setExposureValue('$204k');
        setCurrentAction('REVIEW');
      }, 4000);

      setTimeout(() => {
        setSpikeActive(false);
        setExposureValue('$89k');
        setCurrentAction('RATE LIMIT');
      }, 7000);

      setTimeout(() => {
        setExposureValue('$12k');
        setCurrentAction('MONITOR');
      }, 10000);
    };

    const interval = setInterval(cycleSpike, 12000);
    cycleSpike();

    return () => clearInterval(interval);
  }, []);

  const centerX = dimensions.width / 2;
  const centerY = dimensions.height / 2;

  return (
    <div
      ref={containerRef}
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #0a0f18 0%, #060910 100%)',
        borderRadius: 12,
        border: '1px solid rgba(139, 156, 180, 0.12)',
      }}
      aria-label="Risk intelligence flow visualization"
    >
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: 'radial-gradient(circle, rgba(139, 156, 180, 0.08) 1px, transparent 1px)',
        backgroundSize: '24px 24px',
        pointerEvents: 'none',
      }} />

      <div style={{ position: 'absolute', left: '8%', top: '15%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, zIndex: 2 }}>
        <span style={{ fontSize: 18, color: '#3b82f6' }}>●</span>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', color: '#64748b', whiteSpace: 'nowrap' }}>TRANSACTIONS</span>
      </div>

      <div style={{ position: 'absolute', left: '25%', top: '8%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, zIndex: 2 }}>
        <span style={{ fontSize: 18, color: '#8b5cf6' }}>◉</span>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', color: '#64748b', whiteSpace: 'nowrap' }}>FRAUD SIGNALS</span>
        <SignalPulse delay={0} />
        <SignalPulse delay={0.6} />
      </div>

      <div style={{ position: 'absolute', left: '50%', top: '50%', transform: 'translate(-50%, -50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, zIndex: 3 }}>
        <div style={{ position: 'relative', width: 80, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 32px rgba(99, 102, 241, 0.4)',
            zIndex: 3,
          }}>
            <span style={{ fontSize: 20, color: 'white' }}>◈</span>
          </div>
          <div style={{
            position: 'absolute',
            width: 64,
            height: 64,
            borderRadius: '50%',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            animation: 'rf-ring-pulse 3s ease-in-out infinite',
          }} />
          <div style={{
            position: 'absolute',
            width: 96,
            height: 96,
            borderRadius: '50%',
            border: '1px solid rgba(99, 102, 241, 0.15)',
            animation: 'rf-ring-pulse 3s ease-in-out infinite 0.5s',
          }} />
          <div style={{
            position: 'absolute',
            width: 128,
            height: 128,
            borderRadius: '50%',
            border: '1px solid rgba(99, 102, 241, 0.1)',
            animation: 'rf-ring-pulse 3s ease-in-out infinite 1s',
          }} />
        </div>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', color: '#64748b' }}>RISK ENGINE</span>
      </div>

      <div style={{ position: 'absolute', right: '8%', top: '15%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, zIndex: 2 }}>
        <span style={{ fontSize: 18, color: '#f97316' }}>▲</span>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', color: '#64748b', whiteSpace: 'nowrap' }}>MERCHANT SPIKE</span>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 3, height: 48, marginTop: 4 }}>
          {[20, 35, 28, 45, 62, 78, 95, 88, 92].map((h, i) => (
            <motion.div
              key={i}
              style={{
                width: 6,
                background: 'linear-gradient(to top, #f97316, #fbbf24)',
                borderRadius: 2,
                opacity: h > 50 ? 1 : 0.4,
              }}
              animate={{ height: h }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
            />
          ))}
        </div>
      </div>

      <AnimatePresence>
        {spikeActive && (
          <motion.div
            style={{
              position: 'absolute',
              right: '22%',
              top: '30%',
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 12px',
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 6,
              zIndex: 4,
            }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.3 }}
          >
            <span style={{ fontSize: 10, color: '#ef4444' }}>▲</span>
            <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.1em', color: '#ef4444' }}>SPIKE DETECTED</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div style={{ position: 'absolute', right: '5%', bottom: '20%', zIndex: 2 }}>
        <ExposureMeter value={exposureValue} />
      </div>

      <div style={{ position: 'absolute', left: '50%', bottom: '10%', transform: 'translateX(-50%)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, zIndex: 2 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <ActionCard action="MONITOR" active={currentAction === 'MONITOR'} />
          <ActionCard action="REVIEW" active={currentAction === 'REVIEW'} />
          <ActionCard action="RATE LIMIT" active={currentAction === 'RATE LIMIT'} />
        </div>
        <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.12em', color: '#64748b', marginTop: 4 }}>DEFENSIVE ACTION</span>
      </div>

      <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', zIndex: 1 }}>
        <svg width={dimensions.width} height={dimensions.height} style={{ position: 'absolute', top: 0, left: 0 }}>
          <defs>
            <linearGradient id="flowGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.5" />
            </linearGradient>
            <linearGradient id="flowGrad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#6366f1" stopOpacity="0.6" />
            </linearGradient>
          </defs>

          <motion.path
            d={`M ${dimensions.width * 0.15} ${dimensions.height * 0.2} Q ${dimensions.width * 0.3} ${dimensions.height * 0.35} ${centerX} ${centerY}`}
            stroke="url(#flowGrad1)"
            strokeWidth="2"
            fill="none"
            strokeDasharray="6 4"
            animate={{ pathLength: [0, 1, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          />

          <motion.path
            d={`M ${centerX} ${centerY - 40} L ${dimensions.width * 0.75} ${dimensions.height * 0.18}`}
            stroke="url(#flowGrad2)"
            strokeWidth="2"
            fill="none"
            strokeDasharray="6 4"
            animate={{ pathLength: [0, 1, 1] }}
            transition={{ duration: 2, repeat: Infinity, ease: 'linear', delay: 0.5 }}
          />

          <motion.path
            d={`M ${dimensions.width * 0.85} ${dimensions.height * 0.22} L ${dimensions.width * 0.85} ${dimensions.height * 0.75}`}
            stroke="#ef4444"
            strokeWidth="2"
            fill="none"
            strokeDasharray="4 4"
            animate={{ opacity: spikeActive ? [0.3, 0.8, 0.3] : 0.3 }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
          />

          <motion.path
            d={`M ${centerX} ${centerY + 40} L ${centerX} ${dimensions.height * 0.85}`}
            stroke="#22c55e"
            strokeWidth="2"
            fill="none"
            strokeDasharray="4 4"
            animate={{ pathLength: [0, 1, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'linear', delay: 0.3 }}
          />
        </svg>
      </div>

      <style>{`
        @keyframes rf-ring-pulse {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 0.6; transform: scale(1.05); }
        }
        @media (prefers-reduced-motion: reduce) {
          .rf-engine-ring, .rf-tx-dot, .rf-signal, .rf-spike-indicator, .rf-exposure, .rf-action-card, .rf-spike-bar {
            animation: none !important;
          }
        }
      `}</style>
    </div>
  );
}
