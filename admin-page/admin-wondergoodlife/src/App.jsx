import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ExcelUpload from './pages/ExcelUpload';
import StagingBrandList from './pages/StagingBrandList';
import VersionList from './pages/VersionList';
import VersionDataManagementRefactored from './pages/VersionDataManagement';
import UserManagement from './pages/UserManagement';
import UserProfile from './pages/UserProfile';
import PermissionManagement from './pages/PermissionManagement';
import MainDBStatus from './pages/MainDBStatus';

function App() {
  return (
    <Router>
      <Routes>
        {/* 로그인/회원가입 - 인증 불필요 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* 메인 애플리케이션 - 인증 필요 (ProtectedRoute로 보호) */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="excel-upload" element={<ExcelUpload />} />
          <Route path="staging-brands" element={<StagingBrandList />} />
          <Route path="versions" element={<VersionList />} />
          <Route path="version-data" element={<VersionDataManagementRefactored />} />
          <Route path="user-management" element={<UserManagement />} />
          <Route path="user-profile" element={<UserProfile />} />
          <Route path="permission-management" element={<PermissionManagement />} />
          <Route path="main-db-status" element={<MainDBStatus />} />
        </Route>

        {/* 404 - 로그인으로 리다이렉트 */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
