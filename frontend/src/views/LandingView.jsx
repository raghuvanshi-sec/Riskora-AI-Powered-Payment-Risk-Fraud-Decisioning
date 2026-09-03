import './landing.css';

import Navbar from '../components/landing/Navbar';
import Hero from '../components/landing/Hero';
import CredibilityStrip from '../components/landing/CredibilityStrip';
import FeaturesSection from '../components/landing/FeaturesSection';
import PipelineSection from '../components/landing/PipelineSection';
import ExposureSection from '../components/landing/ExposureSection';
import ActionsSection from '../components/landing/ActionsSection';
import MetricsSection from '../components/landing/MetricsSection';
import ArchitectureSection from '../components/landing/ArchitectureSection';
import RiskDecisionSimulator from '../components/landing/RiskDecisionSimulator';
import Footer from '../components/landing/Footer';

export default function LandingView() {
  return (
    <div className="landing">
      <Navbar />
      <main>
        <Hero />
        <CredibilityStrip />
        <FeaturesSection />
        <PipelineSection />
        <ExposureSection />
        <ActionsSection />
        <MetricsSection />
        <ArchitectureSection />
        <RiskDecisionSimulator />
      </main>
      <Footer />
    </div>
  );
}
