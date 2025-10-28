import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Repositories from './pages/Repositories';
import CodeReview from './pages/CodeReview';
import ManualAnalysis from './pages/ManualAnalysis';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/repositories" element={<Repositories />} />
          <Route path="/review/:sessionId" element={<CodeReview />} />
          <Route path="/manual" element={<ManualAnalysis />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
