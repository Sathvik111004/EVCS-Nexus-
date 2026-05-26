import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Zap, Building2, Leaf, Settings, ArrowLeft, Info, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { getRecommendation, simulateScenario } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [selectedCity, setSelectedCity] = useState('');
  const [numChargers, setNumChargers] = useState(5);
  const [loading, setLoading] = useState(false);
  const [showScenario, setShowScenario] = useState(false);
  
  // Real-world calibration parameters (Now strictly used ONLY for the simulator, not the base analysis)
  const [scenarioParams, setScenarioParams] = useState({
    chargerCost: 15.0, 
    utilizationHours: 6, 
    electricityCost: 8.5, 
    chargingPrice: 18.0   
  });

  // State for calculated economics
  const [baseEcon, setBaseEcon] = useState(null);
  const [simEcon, setSimEcon] = useState(null);
  const [recommendationMeta, setRecommendationMeta] = useState(null);

  // FIX 1: Added Vellore to the hardcoded list so it matches your backend
  const cities = {
    tier1: ["Ahmedabad", "Bengaluru", "Chennai", "Delhi", "Hyderabad", "Kolkata", "Mumbai", "Pune"],
    tier2: ["Agra", "Ajmer", "Amritsar", "Bhopal", "Bhubaneswar", "Chandigarh", "Coimbatore", "Dehradun", "Guwahati", "Indore", "Jabalpur", "Jaipur", "Jalandhar", "Jodhpur", "Kanpur", "Kochi", "Lucknow", "Ludhiana", "Madurai", "Meerut", "Nagpur", "Nashik", "Patna", "Raipur", "Rajkot", "Ranchi", "Surat", "Thiruvananthapuram", "Vadodara", "Varanasi", "Vijayawada", "Visakhapatnam"],
    tier3: ["Ahmednagar", "Aligarh", "Alwar", "Anand", "Bathinda", "Bilaspur", "Dhule", "Gandhinagar", "Haldwani", "Hisar", "Hosur", "Jalgaon", "Karnal", "Kollam", "Kurnool", "Mathura", "Panipat", "Rohtak", "Shimla", "Udaipur","Warangal", "Vellore"]
  };
  const allCities = [...cities.tier1, ...cities.tier2, ...cities.tier3].sort();

  // Smart Formatter for Payback Period
  const formatPayback = (years) => {
    if (years === Infinity) return "No Return";
    if (years < 1) {
      const months = Math.max(1, Math.round(years * 12));
      return `${months} ${months === 1 ? 'Month' : 'Months'}`;
    }
    const y = Math.floor(years);
    const m = Math.round((years - y) * 12);
    return m > 0 ? `${y} Yrs ${m} Mos` : `${y} Years`;
  };

  const handleGetRecommendation = async () => {
    if (!selectedCity) return toast.error('Please select a city');
    setLoading(true);
    try {
      // Fetch AI Meta Data & Economics from backend
      const data = await getRecommendation(selectedCity, numChargers);
      setRecommendationMeta(data);
      
      // FIX 2: Stop overriding the backend! 
      // Map the backend's absolute INR data to your UI's Crores format (1 Crore = 10,000,000 INR)
      const backendEcon = data.economics;
      setBaseEcon({
        capexCr: backendEcon.capex.total / 10000000,
        profitCr: backendEcon.financial.annual_profit / 10000000,
        roi: backendEcon.financial.roi_percentage,
        payback: backendEcon.financial.payback_years,
        dailyRev: backendEcon.financial.annual_revenue / 365,
        dailyOpEx: backendEcon.financial.annual_opex / 365,
        co2: backendEcon.esg.co2_avoided_tonnes
      });
      
      setStep(2);
      toast.success('AI Analysis & Economics Synchronized');
    } catch (error) {
      console.error(error);
      toast.error('ML Engine Offline or Error');
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateScenario = async () => {
    setLoading(true);
    try {
      // FIX 3: Call the actual backend simulation endpoint instead of the local fake math
      const simData = await simulateScenario(
        selectedCity,
        numChargers,
        scenarioParams.chargerCost,
        scenarioParams.utilizationHours,
        scenarioParams.electricityCost,
        scenarioParams.chargingPrice
      );
      
      const backendSimEcon = simData.results;
      setSimEcon({
        capexCr: backendSimEcon.capex.total / 10000000,
        profitCr: backendSimEcon.financial.annual_profit / 10000000,
        roi: backendSimEcon.financial.roi_percentage,
        payback: backendSimEcon.financial.payback_years,
        dailyRev: backendSimEcon.financial.annual_revenue / 365,
        dailyOpEx: backendSimEcon.financial.annual_opex / 365,
        co2: backendSimEcon.esg.co2_avoided_tonnes
      });
      
      toast.success('Simulation Constraints Applied');
    } catch {
      toast.error('Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  // Dynamic Chart Data
  const chartData = useMemo(() => {
    if (!baseEcon) return [];
    return [
      { name: 'Daily OpEx', value: baseEcon.dailyOpEx },
      { name: 'Daily Revenue', value: baseEcon.dailyRev },
      { name: 'Net Daily Profit', value: baseEcon.dailyRev - baseEcon.dailyOpEx },
    ];
  }, [baseEcon]);

  const downloadReport = () => {
    if (!recommendationMeta || !baseEcon) return;
    const blob = new Blob(
      [`EVCS NEXUS INFRASTRUCTURE REPORT\n\nLocation: ${recommendationMeta.city} (${recommendationMeta.locality})\nStations: ${numChargers}\n\n--- FINANCIALS ---\nTotal CAPEX: ₹${baseEcon.capexCr.toFixed(2)} Crores\nAnnual Profit: ₹${baseEcon.profitCr.toFixed(2)} Crores\nEstimated ROI: ${baseEcon.roi.toFixed(1)}%\nPayback Period: ${formatPayback(baseEcon.payback)}\n\n--- ESG IMPACT ---\nCO2 Avoided: ${baseEcon.co2} Tonnes/Year`],
      { type: "text/plain" }
    );
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `EVCS_Report_${recommendationMeta.city}.txt`;
    link.click();
    toast.success('Report Downloaded');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-cyan-100 pb-20">
      
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-md shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2 cursor-pointer group" onClick={() => navigate('/')}>
            <div className="p-1.5 bg-slate-900 rounded-lg group-hover:scale-110 transition-transform">
              <Zap className="text-white w-5 h-5" />
            </div>
            <h1 className="font-black text-xl tracking-tighter">EVCS <span className="text-cyan-600">NEXUS</span></h1>
          </div>
          
          {step === 2 && (
            <div className="flex items-center gap-4">
              <button onClick={() => setShowScenario(true)} className="text-sm font-bold text-slate-500 hover:text-slate-900 flex items-center gap-2 transition-colors">
                <Settings size={16} /> Simulator
              </button>
              <button onClick={downloadReport} className="text-sm font-bold text-slate-500 hover:text-slate-900 flex items-center gap-2 transition-colors">
                Export Data
              </button>
              <button onClick={() => {setStep(1); setSimEcon(null);}} className="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 rounded-xl text-sm font-bold transition-colors flex items-center gap-2 border border-slate-200 shadow-sm">
                <ArrowLeft size={16} /> New Analysis
              </button>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-10">
        <AnimatePresence mode="wait">
          {step === 1 ? (
            <motion.div key="input" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="max-w-xl mx-auto mt-10">
              <div className="bg-white p-10 rounded-[2.5rem] border border-slate-200 shadow-xl shadow-slate-200/50">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-black mb-2 tracking-tight">Deploy AI Node</h2>
                  <p className="text-slate-500 font-medium">Configure urban demand parameters.</p>
                </div>

                <div className="space-y-6">
                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase tracking-widest text-slate-400">Target City</label>
                    <select value={selectedCity} onChange={(e) => setSelectedCity(e.target.value)} className="w-full bg-slate-50 border border-slate-200 p-4 rounded-2xl font-bold outline-none focus:ring-2 focus:ring-cyan-500/20 text-slate-700 cursor-pointer">
                      <option value="">Select Urban Center</option>
                      {allCities.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-black uppercase tracking-widest text-slate-400">Total Charger Units</label>
                    <input type="number" min="1" value={numChargers} onChange={(e) => setNumChargers(parseInt(e.target.value))} className="w-full bg-slate-50 border border-slate-200 p-4 rounded-2xl font-bold outline-none focus:ring-2 focus:ring-cyan-500/20" />
                  </div>

                  <button onClick={handleGetRecommendation} disabled={loading} className="w-full bg-slate-900 text-white py-5 rounded-2xl font-black text-lg shadow-lg hover:bg-black transition-all disabled:opacity-50 mt-4">
                    {loading ? "Simulating Topology..." : "Analyze Demand →"}
                  </button>
                </div>
              </div>
            </motion.div>
          ) : (
            <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              
              {/* Row 1: City & Profitability */}
              <div className="grid lg:grid-cols-4 gap-6">
                <div className="lg:col-span-3 bg-white p-8 rounded-[2rem] border border-slate-200 flex flex-col justify-center shadow-sm">
                  <div className="flex items-center gap-3 text-cyan-600 mb-3">
                    <Building2 size={20} />
                    <span className="text-xs font-black uppercase tracking-widest">{recommendationMeta.tier} CLUSTER</span>
                  </div>
                  <h2 className="text-6xl font-black tracking-tight text-slate-900">{recommendationMeta.city}</h2>
                  <p className="text-slate-500 font-bold mt-2 uppercase tracking-widest text-sm">{recommendationMeta.locality} ZONE ANALYSIS</p>
                </div>

                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 flex flex-col items-center justify-center text-center shadow-sm">
                   <div className={`text-5xl font-black mb-2 ${recommendationMeta.profitability === 'Excellent' || recommendationMeta.profitability === 'High' ? 'text-green-500' : 'text-amber-500'}`}>
                    {recommendationMeta.profitability}
                   </div>
                   <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Yield Index</p>
                </div>
              </div>

              {/* Row 2: AI & Hardware */}
              <div className="grid lg:grid-cols-2 gap-6">
                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm">
                  <div className="flex items-center gap-3 mb-6">
                    <Zap className="text-amber-500" />
                    <h3 className="font-black text-xl uppercase tracking-tight">Hardware Specification</h3>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-5 bg-slate-50 rounded-2xl border border-slate-100">
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Vehicles</p>
                      <p className="font-bold text-slate-800 text-lg">{recommendationMeta.classification.vehicle_type}</p>
                    </div>
                    <div className="p-5 bg-slate-50 rounded-2xl border border-slate-100">
                      <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Unit Power</p>
                      <p className="font-bold text-slate-800 text-lg">{recommendationMeta.classification.charger_power_kw} kW</p>
                    </div>
                  </div>
                </div>

                <div className="bg-cyan-50 p-8 rounded-[2rem] border border-cyan-100 shadow-sm">
                  <div className="flex items-center gap-3 mb-4 text-cyan-700">
                    <Info size={20} />
                    <h3 className="font-black text-xl uppercase tracking-tight">AI Reasoning</h3>
                  </div>
                  <p className="text-cyan-900 font-medium leading-relaxed text-lg">
                    {recommendationMeta.ml_insights.recommendation_reason}
                  </p>
                </div>
              </div>

              {/* Row 3: Crores & Months Financials */}
              <div className="grid lg:grid-cols-4 gap-6">
                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm">
                  <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Initial CAPEX</p>
                  <h3 className="text-4xl font-black tracking-tight text-slate-900">₹{baseEcon.capexCr.toFixed(2)} <span className="text-base text-slate-400 font-bold ml-1">Cr</span></h3>
                </div>

                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm">
                  <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Annual Profit</p>
                  <h3 className="text-4xl font-black tracking-tight text-green-600">₹{baseEcon.profitCr.toFixed(2)} <span className="text-base text-green-600/60 font-bold ml-1">Cr</span></h3>
                </div>

                <div className="bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm">
                  <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Est. ROI</p>
                  <h3 className="text-4xl font-black tracking-tight text-blue-600">{baseEcon.roi.toFixed(1)}%</h3>
                </div>

                <div className="bg-slate-900 p-8 rounded-[2rem] text-white shadow-xl shadow-slate-900/20">
                  <p className="text-xs font-black text-cyan-400/70 uppercase tracking-widest mb-2">Payback Period</p>
                  <h3 className="text-4xl font-black tracking-tight text-cyan-400">
                    {formatPayback(baseEcon.payback)}
                  </h3>
                </div>
              </div>

              {/* Row 4: Recharts & ESG */}
              <div className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white p-8 rounded-[2rem] border border-slate-200 shadow-sm min-h-[300px]">
                  <h4 className="font-black uppercase tracking-widest text-slate-400 text-xs mb-8 flex items-center gap-2">
                    <BarChart3 size={16} /> Daily Revenue vs Operating Cost (₹)
                  </h4>
                  <div className="h-[220px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12, fontWeight: 700}} dy={10} />
                        <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '16px', border: '1px solid #e2e8f0', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)', fontWeight: 'bold'}} formatter={(value) => `₹${Math.round(value).toLocaleString()}`} />
                        <Bar dataKey="value" radius={[8, 8, 0, 0]} maxBarSize={60}>
                          {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index === 2 ? '#10b981' : index === 1 ? '#3b82f6' : '#94a3b8'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-emerald-50 p-8 rounded-[2rem] border border-emerald-100 flex flex-col justify-between shadow-sm">
                  <div>
                    <Leaf className="text-emerald-600 mb-4 w-8 h-8" />
                    <h4 className="text-xs font-black text-emerald-800 uppercase tracking-widest">ESG Impact Score</h4>
                  </div>
                  <div>
                    <p className="text-6xl font-black text-emerald-700 tracking-tighter mb-1">{Math.round(baseEcon.co2)}</p>
                    <p className="text-sm font-bold text-emerald-600 uppercase tracking-widest">Tonnes CO₂ Saved / Year</p>
                  </div>
                </div>
              </div>

            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Simulator Modal */}
      <AnimatePresence>
        {showScenario && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setShowScenario(false)} className="absolute inset-0 bg-slate-900/30 backdrop-blur-sm" />
            <motion.div initial={{ scale: 0.95, opacity: 0, y: 20 }} animate={{ scale: 1, opacity: 1, y: 0 }} exit={{ scale: 0.95, opacity: 0, y: 20 }} className="relative bg-white w-full max-w-2xl rounded-[2.5rem] p-10 shadow-2xl border border-slate-200">
               <h2 className="text-3xl font-black mb-8 tracking-tight">Dynamic Simulator</h2>
               
               <div className="grid grid-cols-2 gap-5 mb-8">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Charger Cost (₹ Lakhs)</label>
                    <input type="number" step="1" value={scenarioParams.chargerCost} onChange={e => setScenarioParams({...scenarioParams, chargerCost: +e.target.value})} className="w-full bg-slate-50 border border-slate-200 p-4 rounded-xl font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Daily Util. (Hours)</label>
                    <input type="number" min="1" max="24" value={scenarioParams.utilizationHours} onChange={e => setScenarioParams({...scenarioParams, utilizationHours: +e.target.value})} className="w-full bg-slate-50 border border-slate-200 p-4 rounded-xl font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Electricity (₹/Unit)</label>
                    <input type="number" step="0.5" value={scenarioParams.electricityCost} onChange={e => setScenarioParams({...scenarioParams, electricityCost: +e.target.value})} className="w-full bg-slate-50 border border-slate-200 p-4 rounded-xl font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400">Charge Price (₹/Unit)</label>
                    <input type="number" step="0.5" value={scenarioParams.chargingPrice} onChange={e => setScenarioParams({...scenarioParams, chargingPrice: +e.target.value})} className="w-full bg-slate-50 border border-slate-200 p-4 rounded-xl font-bold outline-none focus:ring-2 focus:ring-purple-500/20 transition-all" />
                  </div>
               </div>
               
               <button onClick={handleSimulateScenario} disabled={loading} className="w-full bg-purple-600 text-white py-4 rounded-xl font-black text-lg mb-6 hover:bg-purple-700 transition-colors disabled:opacity-50 shadow-lg shadow-purple-600/20">
                 {loading ? "Simulating Constraints..." : "Run Economic Simulation"}
               </button>

               {/* Simulated Results Block */}
               <AnimatePresence>
                 {simEcon && (
                   <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="grid grid-cols-3 gap-4 border-t border-slate-100 pt-6 mb-6">
                     <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200">
                       <p className="text-[10px] font-black uppercase tracking-widest text-slate-400">Sim CAPEX</p>
                       <p className="text-2xl font-black text-slate-900 mt-1">₹{simEcon.capexCr.toFixed(2)}<span className="text-sm text-slate-400 ml-1">Cr</span></p>
                     </div>
                     <div className="bg-purple-50 p-5 rounded-2xl border border-purple-100">
                       <p className="text-[10px] font-black uppercase tracking-widest text-purple-400">Sim ROI</p>
                       <p className="text-2xl font-black text-purple-600 mt-1">{simEcon.roi.toFixed(1)}%</p>
                     </div>
                     <div className="bg-cyan-50 p-5 rounded-2xl border border-cyan-100">
                       <p className="text-[10px] font-black uppercase tracking-widest text-cyan-500">Sim Payback</p>
                       <p className="text-2xl font-black text-cyan-600 mt-1">{formatPayback(simEcon.payback)}</p>
                     </div>
                   </motion.div>
                 )}
               </AnimatePresence>

               <button onClick={() => setShowScenario(false)} className="w-full text-slate-500 font-bold hover:text-slate-900 transition-colors py-2">Close Simulator</button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;