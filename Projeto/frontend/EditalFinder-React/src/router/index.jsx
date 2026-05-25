import { ENABLE_CONSULTOR_WORKSPACE, ENABLE_SCIENTIFIC_WORKSPACE } from '../config/env';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login from '../pages/Login';
import AuthCallback from '../pages/AuthCallback';
import Dashboard from '../pages/Dashboard';
import EditaisPage from '../pages/EditaisPage';
import Cadastros from '../pages/Cadastros';
import RadarFomento from '../pages/RadarFomento';
import IndiceCompatibilidade from '../pages/IndiceCompatibilidade';
import EditalDetalhes from '../pages/EditalDetalhes';
import Noticias from '../pages/Noticias';
import Pesquisas from '../pages/Pesquisas';
import PortaisEstrategicosPage from '../pages/PortaisEstrategicos/PortaisEstrategicosPage';
import ConcursosPage from '../pages/Concursos/ConcursosPage';
import ConsultorWorkspace from '../pages/ConsultorWorkspace';
import ScientificWorkspace from '../pages/ScientificWorkspace';
import ProtectedRoute from './ProtectedRoute';
import { withAppErrorBoundary } from './withAppErrorBoundary';
import { SCIENTIFIC_LOCAL_STORAGE_KEYS } from '../utils/scientific/clearScientificWorkspaceLocalCache';

export default function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/login"
        element={withAppErrorBoundary('user_report', 'login', <Login />)}
      />
      <Route
        path="/auth/callback"
        element={withAppErrorBoundary('user_report', 'auth_callback', <AuthCallback />)}
      />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('dashboard', 'Dashboard', <Dashboard />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/editais"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('editais', 'Editais', <EditaisPage />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/cadastros"
        element={
          <ProtectedRoute requiredPermission="canViewCadastros">
            {withAppErrorBoundary('cadastros', 'cadastros', <Cadastros />)}
          </ProtectedRoute>
        }
      />
      {ENABLE_CONSULTOR_WORKSPACE ? (
        <Route
          path="/workspace-consultor"
          element={
            <ProtectedRoute requiredPermission="canViewCadastros">
              {withAppErrorBoundary('workspace_consultor', 'workspace_consultor', <ConsultorWorkspace />)}
            </ProtectedRoute>
          }
        />
      ) : (
        <Route path="/workspace-consultor" element={<Navigate to="/dashboard" replace />} />
      )}
      {ENABLE_SCIENTIFIC_WORKSPACE ? (
        <Route
          path="/workspace-cientifico"
          element={
            <ProtectedRoute>
              {withAppErrorBoundary('workspace_cientifico', 'workspace_cientifico', <ScientificWorkspace />, {
                fallbackTitle: 'Não foi possível carregar o Workspace Científico',
                fallbackMessage:
                  'Ocorreu um erro ao renderizar esta página. Seus dados no servidor não foram alterados.',
                allowClearLocalCache: true,
                clearLocalCacheKeys: SCIENTIFIC_LOCAL_STORAGE_KEYS,
              })}
            </ProtectedRoute>
          }
        />
      ) : (
        <Route path="/workspace-cientifico" element={<Navigate to="/dashboard" replace />} />
      )}
      <Route
        path="/radar-fomento"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('radar', 'radar_fomento', <RadarFomento />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/indice"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('editais', 'indice', <IndiceCompatibilidade />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/noticias"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('noticias', 'noticias', <Noticias />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/pesquisas"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('pesquisas', 'pesquisas', <Pesquisas />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/portais-estrategicos"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('portais', 'portais', <PortaisEstrategicosPage />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/concursos"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('concursos', 'concursos', <ConcursosPage />)}
          </ProtectedRoute>
        }
      />
      <Route
        path="/edital/:id"
        element={
          <ProtectedRoute>
            {withAppErrorBoundary('editais', 'edital_detalhes', <EditalDetalhes />)}
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
