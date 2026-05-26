import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Zap, TrendingUp, ArrowRight, Database, ShieldCheck, Target, Cpu } from 'lucide-react';
import RetroGrid from '../components/RetroGrid';
import FigmaFeatureSection from '../components/FigmaFeatureSection';

const Landing = () => {
  return (
    <div className="bg-white text-slate-900 min-h-screen font-sans selection:bg-cyan-100 overflow-x-hidden">
      
      {/* 1. STICKY NAVIGATION */}
      <nav className="fixed top-0 w-full z-[100] bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2 font-black text-xl tracking-tighter">
            <div className="p-1.5 bg-slate-900 rounded-lg">
              <Zap className="text-white w-5 h-5" />
            </div>
            EVCS <span className="text-cyan-600">NEXUS</span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-bold text-slate-500">
            <a href="#problem" className="hover:text-slate-900 transition-colors">The Problem</a>
            <a href="#features" className="hover:text-slate-900 transition-colors">AI Engine</a>
            <a href="#data" className="hover:text-slate-900 transition-colors">Architecture</a>
          </div>
          <Link to="/dashboard" className="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-black transition-all">
            Launch App
          </Link>
        </div>
      </nav>

      {/* 2. HERO SECTION */}
      <section className="relative pt-32 pb-20 flex items-center justify-center px-6 overflow-hidden">
        <RetroGrid className="opacity-[0.06]" />
        <div className="absolute w-[600px] h-[600px] bg-cyan-100/40 blur-[120px] top-[-10%] left-[-5%] -z-10" />
        
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-5xl z-10"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-50 border border-slate-200 text-slate-500 text-xs font-bold uppercase tracking-widest mb-8">
            ✨ Powered by LOOCV-Validated Machine Learning
          </div>
          <h1 className="text-6xl md:text-8xl font-black leading-[1.05] tracking-tight text-slate-900">
            India’s EV Revolution 
            <br />
            <span className="bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
              Needs Precision.
            </span>
          </h1>
          <p className="mt-8 text-xl md:text-2xl text-slate-500 max-w-2xl mx-auto font-medium">
            Transform the national charging gap into a high-yield asset. Optimize station placement using real-time economic modeling.
          </p>
          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-6">
            <Link to="/dashboard" className="group inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-slate-900 font-bold text-white shadow-xl hover:scale-105 transition-all">
              Launch Platform <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </motion.div>
      </section>

      {/* 3. TECH LOGO STRIP */}
      <section className="py-12 border-y border-slate-100 bg-slate-50/30">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-center items-center gap-10 md:gap-20 opacity-40 grayscale">
          <span className="font-black text-xl tracking-tighter">REACT</span>
          <span className="font-black text-xl tracking-tighter">FASTAPI</span>
          <span className="font-black text-xl tracking-tighter">SCIKIT-LEARN</span>
          <span className="font-black text-xl tracking-tighter">TAILWIND</span>
          <span className="font-black text-xl tracking-tighter">PANDAS</span>
        </div>
      </section>

      {/* 4. THE CRISIS SECTION */}
      <section id="problem" className="py-32 px-6">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-20 items-center">
          <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
            <h2 className="text-5xl font-black mb-8 leading-tight text-slate-900">Turn a National Crisis into a Local Asset.</h2>
            <p className="text-xl text-slate-500 leading-relaxed mb-10">
              With over 135 EVs for every 1 public charger, India faces a massive infrastructure bottleneck. EVCS Nexus removes the guesswork from urban planning.
            </p>
            <div className="inline-flex items-center gap-5 bg-white border border-red-100 p-8 rounded-[2rem] shadow-sm">
              <TrendingUp className="text-red-500 w-10 h-10" />
              <div>
                <p className="text-4xl font-black text-red-600">1 : 135</p>
                <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Charger to EV Ratio</p>
              </div>
            </div>
          </motion.div>
          
          {/* UPDATED: Data Visualization Image Block */}
          <div className="relative p-2 bg-white border border-slate-200 rounded-[2.5rem] shadow-2xl">
             <img 
               src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=1000" 
               alt="EVCS Nexus Analytics Dashboard" 
               className="rounded-[2rem] w-full h-auto object-cover grayscale-[0.1]"
             />
             <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 to-transparent rounded-[2.5rem] pointer-events-none" />
          </div>
        </div>
      </section>

      {/* 5. FIGMA FEATURE SECTION (3 Catchy Entities) */}
      <section id="features">
        <FigmaFeatureSection />
      </section>

      {/* 6. RIGOROUS DATA ARCHITECTURE (Technical Proof) */}
      <section id="data" className="py-32 bg-slate-50 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-black text-slate-900 mb-6">Rigorous Data Architecture</h2>
            <p className="text-xl text-slate-500 max-w-2xl mx-auto">Our engine doesn't just calculate; it simulates reality using high-fidelity data extraction.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: <Database />, title: "8-Point Extraction", desc: "Evaluates stations based on peak-to-average ratios and idle hour margins." },
              { icon: <ShieldCheck />, title: "LOOCV Validated", desc: "Engines strictly validated via Leave-One-Out Cross-Validation to prevent regional bias." },
              { icon: <Cpu />, title: "Domain Mapping", desc: "Maps raw clusters to Indian contextual data for specialized charger deployment." }
            ].map((item, i) => (
              <motion.div key={i} whileHover={{ y: -10 }} className="p-10 bg-white border border-slate-200 rounded-[2rem] shadow-sm">
                <div className="text-cyan-600 mb-6">{item.icon}</div>
                <h4 className="text-xl font-bold mb-4">{item.title}</h4>
                <p className="text-slate-500 leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 7. FINAL CALL TO ACTION */}
      <section className="py-40 bg-slate-950 relative overflow-hidden text-center mx-6 my-12 rounded-[3rem]">
        <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,_#22d3ee20_0%,_transparent_70%)]" />
        <div className="relative z-10 max-w-4xl mx-auto px-6">
          <h2 className="text-5xl md:text-7xl font-black text-white mb-8">Stop Guessing.<br />Start Planning.</h2>
          <p className="text-xl text-slate-400 mb-12 max-w-2xl mx-auto">
            Deploy your first virtual node today and see the economics unfold in real-time.
          </p>
          <Link to="/dashboard" className="inline-flex items-center gap-3 px-12 py-6 rounded-2xl bg-white text-slate-950 font-black text-xl hover:scale-105 transition-all shadow-[0_0_50px_rgba(255,255,255,0.2)]">
            Access Dashboard <Zap className="w-6 h-6" />
          </Link>
        </div>
      </section>

      <footer className="py-12 text-center text-slate-400 text-sm">
        © 2026 EVCS Nexus • Designed in Figma • Powered by AI
      </footer>
    </div>
  );
};

export default Landing;