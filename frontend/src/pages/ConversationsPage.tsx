import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../hooks';
import { fetchConversations, selectConversation, clearError } from '../store/slices/conversationsSlice';
import './ConversationsPage.css';

const ConversationsPage = () => {
  const dispatch = useAppDispatch();
  const { conversations, selectedConversation, loading, error } = useAppSelector((state) => state.conversations);

  useEffect(() => {
    dispatch(fetchConversations());
  }, [dispatch]);

  const handleSelectConversation = (conversation: any) => {
    dispatch(selectConversation(conversation));
  };

  const handleClearError = () => {
    dispatch(clearError());
  };

  return (
    <div className="conversations-page">
      <div className="page-header">
        <h1>会话管理</h1>
        <p>创建、配置和管理会话</p>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={handleClearError}>关闭</button>
        </div>
      )}

      <div className="conversations-container">
        <div className="conversations-list">
          <h2>会话列表</h2>
          <button className="btn-primary">创建会话</button>

          {loading ? (
            <div className="loading">加载中...</div>
          ) : conversations.length === 0 ? (
            <div className="empty-state">
              <p>暂无会话</p>
              <p>点击"创建会话"按钮添加第一个会话</p>
            </div>
          ) : (
            <div className="conversations-grid">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`conversation-card ${selectedConversation?.id === conversation.id ? 'selected' : ''}`}
                  onClick={() => handleSelectConversation(conversation)}
                >
                  <div className="conversation-card-header">
                    <h3>{conversation.name}</h3>
                    <span className={`conversation-status conversation-status-${conversation.status}`}>
                      {conversation.status}
                    </span>
                  </div>

                  <div className="conversation-card-body">
                    <p className="conversation-description">{conversation.description}</p>

                    <div className="conversation-meta">
                      <div className="meta-item">
                        <span className="meta-label">智能体 ID:</span>
                        <span className="meta-value">{conversation.agent_id}</span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">创建时间:</span>
                        <span className="meta-value">
                          {new Date(conversation.created_at).toLocaleString()}
                        </span>
                      </div>

                      <div className="meta-item">
                        <span className="meta-label">更新时间:</span>
                        <span className="meta-value">
                          {new Date(conversation.updated_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="conversation-card-footer">
                    <button className="btn-secondary">编辑</button>
                    <button className="btn-danger">删除</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedConversation && (
          <div className="conversation-details">
            <h2>会话详情</h2>

            <div className="detail-section">
              <h3>基本信息</h3>
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">名称:</span>
                  <span className="detail-value">{selectedConversation.name}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">智能体 ID:</span>
                  <span className="detail-value">{selectedConversation.agent_id}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">状态:</span>
                  <span className="detail-value">
                    <span className={`conversation-status conversation-status-${selectedConversation.status}`}>
                      {selectedConversation.status}
                    </span>
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">描述:</span>
                  <span className="detail-value">{selectedConversation.description}</span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">创建时间:</span>
                  <span className="detail-value">
                    {new Date(selectedConversation.created_at).toLocaleString()}
                  </span>
                </div>

                <div className="detail-item">
                  <span className="detail-label">更新时间:</span>
                  <span className="detail-value">
                    {new Date(selectedConversation.updated_at).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h3>配置</h3>
              <pre className="config-code">
                {JSON.stringify(selectedConversation.config, null, 2)}
              </pre>
            </div>

            <div className="detail-section">
              <h3>操作</h3>
              <div className="action-buttons">
                <button className="btn-primary">开始会话</button>
                <button className="btn-secondary">停止会话</button>
                <button className="btn-secondary">查看消息</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationsPage;
