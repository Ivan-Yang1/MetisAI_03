import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks';
import { fetchAgents, selectAgent, clearError } from '../store/slices/agentsSlice';
import './AgentsPage.css';

const AgentsPage = () => {
  const dispatch = useAppDispatch();
  const { agents, selectedAgent, loading, error } = useAppSelector((state) => state.agents);

  useEffect(() => {
    dispatch(fetchAgents());
  }, [dispatch]);

  const handleSelectAgent = (agent: any) => {
    dispatch(selectAgent(agent));
  };

  const handleClearError = () => {
    dispatch(clearError());
  };

  return (
    <div className="agents-page">
      <div className="page-header">
        <h1>智能体管理</h1>
        <p>创建、配置和管理 AI 智能体</p>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={handleClearError}>关闭</button>
        </div>
      )}

      <div className="agents-container">
        <div className="agents-list">
          <h2>智能体列表</h2>
          <button className="btn-primary">创建智能体</button>

          {loading ? (
            <div className="loading">加载中...</div>
          ) : agents.length === 0 ? (
            <div className="empty-state">
              <p>暂无智能体</p>
              <p>点击"创建智能体"按钮添加第一个智能体</p>
            </div>
          ) : (
            <div className="agents-grid">
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className={`agent-card ${selectedAgent?.id === agent.id ? 'selected' : ''}`}
                  onClick={() => handleSelectAgent(agent)}
                >
                  <div className="agent-card-header">
                    <h3>{agent.name}</h3>
                    <span className={`agent-status agent-status-${agent.status}`}>
                      {agent.status}
                    </span>
                  </div>

                  <div className="agent-card-body">
                    <p className="agent-description">{agent.description}</p>

                    <div className="agent-meta">
                      <div className="meta-item">
                        <span className="meta-label">类型:</span>
                        <span className="meta-value">{agent.type}</span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">创建时间:</span>
                        <span className="meta-value">
                          {new Date(agent.created_at).toLocaleString()}
                        </span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">更新时间:</span>
                        <span className="meta-value">
                          {new Date(agent.updated_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="agent-card-footer">
                    <button className="btn-secondary">编辑</button>
                    <button className="btn-danger">删除</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedAgent && (
          <div className="agent-details">
            <h2>智能体详情</h2>

            <div className="detail-section">
              <h3>基本信息</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">名称:</span>
                  <span className="detail-value">{selectedAgent.name}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">类型:</span>
                  <span className="detail-value">{selectedAgent.type}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">状态:</span>
                  <span className="detail-value">
                    <span className={`agent-status agent-status-${selectedAgent.status}`}>
                      {selectedAgent.status}
                    </span>
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">描述:</span>
                  <span className="detail-value">{selectedAgent.description}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">创建时间:</span>
                  <span className="detail-value">
                    {new Date(selectedAgent.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">更新时间:</span>
                  <span className="detail-value">
                    {new Date(selectedAgent.updated_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>配置</h3>
              <pre className="config-code">
                {JSON.stringify(selectedAgent.config, null, 2)}
              </pre>
            </div>

            <div className="detail-section">
              <h3>操作</h3>
              <div className="action-buttons">
                <button className="btn-primary">运行智能体</button>
                <button className="btn-secondary">停止智能体</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentsPage;
