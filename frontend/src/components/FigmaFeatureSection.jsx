import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { BrainCircuit, LineChart, Leaf } from 'lucide-react';

const FigmaFeatureSection = () => {
  const features = [
    {
      title: "ML DRIVEN PLACEMENT",
      icon: <BrainCircuit className="w-8 h-8 text-white" />,
      gradient: "from-green-400 to-green-600",
    },
    {
      title: "FINANCIAL FORECASTING",
      icon: <LineChart className="w-8 h-8 text-white" />,
      gradient: "from-purple-500 to-purple-700",
    },
    {
      title: "SUSTAINABILITY FIRST",
      icon: <Leaf className="w-8 h-8 text-white" />,
      gradient: "from-rose-400 to-rose-600",
    }
  ];

  return (
    <section className="py-24 px-6 bg-white relative overflow-hidden">
      {/* Fixed SVG Grid Background */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none" 
        style={{ 
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23000000' fill-opacity='1' fill-rule='evenodd'%3E%3Cpath d='M0 40L40 40L40 0L0 0L0 40ZM1 39L1 1L39 1L39 39L1 39Z'/%3E%3C/g%3E%3C/svg%3E")` 
        }} 
      />

      <div className="max-w-7xl mx-auto relative z-10 text-center">
        {/* Headline */}
        <motion.h2 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl font-black text-slate-900 mb-8 tracking-tight uppercase"
        >
          Turn the charging gap into a <br className="hidden md:block" /> 
          high-yield asset
        </motion.h2>

        {/* Sub-headline */}
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-lg md:text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed mb-20"
        >
          India's EV market is skyrocketing, yet infrastructure remains the biggest hurdle. 
          EVCS Nexus uses custom Machine Learning pipelines to remove the guesswork. 
          We map Tier 1, 2, and 3 cities to identify the most profitable street corners, 
          predicting your ROI, CAPEX, and payback periods with surgical precision.
        </motion.p>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mt-16 mb-16">
          {features.map((f, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ y: -10 }}
              className="relative group"
            >
              {/* Overlapping Icon Circle */}
              <div className={`absolute -top-10 left-1/2 -translate-x-1/2 w-20 h-20 rounded-full bg-gradient-to-br ${f.gradient} flex items-center justify-center shadow-xl z-20 transition-transform group-hover:scale-110`}>
                {f.icon}
              </div>

              {/* Card Body */}
              <div className="bg-white border border-slate-100 rounded-[2rem] p-12 pt-16 shadow-sm hover:shadow-xl hover:shadow-slate-200/50 transition-all duration-300 h-full flex flex-col items-center justify-center min-h-[200px]">
                <h3 className="text-xl md:text-2xl font-black text-slate-800 text-center uppercase tracking-tight leading-tight">
                  {f.title}
                </h3>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Get Started Button */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <Link 
            to="/dashboard"
            className="inline-block bg-[#1a1a1a] text-white px-12 py-5 rounded-xl font-bold text-lg hover:bg-black transition-all hover:scale-105 active:scale-95 shadow-lg"
          >
            Get Started
          </Link>
        </motion.div>
      </div>
    </section>
  );
};

export default FigmaFeatureSection;