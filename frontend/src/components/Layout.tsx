import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>MetisAI</h1>
        <p>基于 OpenHands 架构的 AI 驱动开发平台</p>
      </header>

      <nav className="app-nav">
        <ul>
          <li>
            <Link
              to="/agents"
              className={isActive('/agents') ? 'active' : ''}
            >
              智能体管理
            </Link>
          </li>
          <li>
            <Link
              to="/conversations"
              className={isActive('/conversations') ? 'active' : ''}
            >
              会话管理
            </Link>
          </li>
        </ul>
      </nav>

      <main className="app-main">
        {children}
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 MetisAI. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Layout;
