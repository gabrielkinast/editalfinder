import { Routes, Route, Navigate } from 'react-router-dom';
import Login from '../pages/Login';
import AuthCallback from '../pages/AuthCallback';
import Dashboard from '../pages/Dashboard';
import Cadastros from '../pages/Cadastros';
import RadarFomento from '../pages/RadarFomento';
import IndiceCompatibilidade from '../pages/IndiceCompatibilidade';
import EditalDetalhes from '../pages/EditalDetalhes';
import Noticias from '../pages/Noticias';
import Pesquisas from '../pages/Pesquisas';
import PortaisEstrategicosPage from '../pages/PortaisEstrategicos/PortaisEstrategicosPage';
import ConcursosPage from '../pages/Concursos/ConcursosPage';
import ProtectedRoute from './ProtectedRoute';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
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
        path="/indice"
        element={
          <ProtectedRoute>
            <IndiceCompatibilidade />
          </ProtectedRoute>
        }
      />
      <Route
        path="/noticias"
        element={
          <ProtectedRoute>
            <Noticias />
          </ProtectedRoute>
        }
      />
      <Route
        path="/pesquisas"
        element={
          <ProtectedRoute>
            <Pesquisas />
          </ProtectedRoute>
        }
      />
      <Route
        path="/portais-estrategicos"
        element={
          <ProtectedRoute>
            <PortaisEstrategicosPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/concursos"
        element={
          <ProtectedRoute>
            <ConcursosPage />
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

