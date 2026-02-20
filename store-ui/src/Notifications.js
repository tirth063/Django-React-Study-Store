import api from "./api";
import React, { useState, useEffect } from 'react';

function Notifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const res = await api.get(`notifications/`);
      setNotifications(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const markAsRead = async (id) => {
    try {
      await api.post(`notifications/${id}/read/`);
      loadNotifications();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Notifications</h2>
      {notifications.length === 0 ? (
        <p className="text-muted">No notifications</p>
      ) : (
        notifications.map(n => (
          <div
            key={n.id}
            className={`card mb-3 ${n.status === 'unread' ? 'border-primary' : ''}`}
          >
            <div className="card-body">
              <p className="mb-2">{n.message}</p>
              <small className="text-muted">{new Date(n.created_at).toLocaleString()}</small>
              {n.status === 'unread' && (
                <button
                  className="btn btn-sm btn-primary ms-3"
                  onClick={() => markAsRead(n.id)}
                >
                  Mark as Read
                </button>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default Notifications;