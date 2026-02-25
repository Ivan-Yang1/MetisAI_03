import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../hooks';
import { fetchMessagesByConversation, clearError } from '../store/slices/messagesSlice';
import './MessagesPage.css';

const MessagesPage = () => {
  const { id } = useParams<{ id: string }>();
  const dispatch = useAppDispatch();
  const { messages, loading, error } = useAppSelector((state) => state.messages);

  useEffect(() => {
    if (id) {
      dispatch(fetchMessagesByConversation(parseInt(id)));
    }
  }, [dispatch, id]);

  const handleSendMessage = () => {
    // 实现发送消息功能
    console.log('发送消息');
  };

  const handleClearError = () => {
    dispatch(clearError());
  };

  return (
    <div className="messages-page">
      <div className="page-header">
        <h1>会话消息</h1>
        <p>查看和发送会话消息</p>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={handleClearError}>关闭</button>
        </div>
      )}

      <div className="messages-container">
        <div className="messages-list">
          <h2>消息列表</h2>

          {loading ? (
            <div className="loading">加载中...</div>
          ) : messages.length === 0 ? (
            <div className="empty-state">
              <p>暂无消息</p>
              <p>发送消息开始对话</p>
            </div>
          ) : (
            <div className="messages-grid">
              {messages.map((message) => (
                <div key={message.id} className={`message-card message-card-${message.role}`}>
                  <div className="message-card-header">
                    <span className="message-role">{message.role}</span>
                    <span className="message-time">
                      {new Date(message.created_at).toLocaleString()}
                    </span>
                  </div>

                  <div className="message-card-body">
                    <p className="message-content">{message.content}</p>
                  </div>

                  {message.metadata && Object.keys(message.metadata).length > 0 && (
                    <div className="message-card-footer">
                      <div className="message-metadata">
                        <pre className="metadata-code">
                          {JSON.stringify(message.metadata, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="message-input">
          <h2>发送消息</h2>

          <div className="input-container">
            <textarea
              placeholder="输入消息内容..."
              className="message-textarea"
            ></textarea>

            <div className="input-actions">
              <button className="btn-primary" onClick={handleSendMessage}>
                发送消息
              </button>
              <button className="btn-secondary">清除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessagesPage;
