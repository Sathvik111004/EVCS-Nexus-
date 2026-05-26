import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
// Delete the imports for Login and Register!

function App() {
  return (
    <BrowserRouter>
      {/* This handles the popup notifications */}
      <Toaster position="top-right" /> 
      
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Dashboard />} />
        
        {/* DELETE the <Route path="/login" /> and <Route path="/register" /> lines */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;