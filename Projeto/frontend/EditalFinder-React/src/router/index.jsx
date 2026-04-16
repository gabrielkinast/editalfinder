import { Routes, Route, Navigate } from 'react-router-dom';
import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import Cadastros from '../pages/Cadastros';
import RadarFomento from '../pages/RadarFomento';
import EditalDetalhes from '../pages/EditalDetalhes';
import ProtectedRoute from './ProtectedRoute';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/cadastros" 
        element={
          <ProtectedRoute requiredPermission="canViewCadastros">
            <Cadastros />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/radar-fomento" 
        element={
          <ProtectedRoute>
            <RadarFomento />
          </ProtectedRoute>
        } 
      />
      <Route
        path="/edital/:id"
        element={
          <ProtectedRoute>
            <EditalDetalhes />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

