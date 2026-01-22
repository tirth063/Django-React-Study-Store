import api from "./api";
import React, { useState, useEffect } from 'react';

function Notifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    loadNotifications();
  }, []);

      const dummyNotifications = [
      {
        id: 1,
        message: "alice_smith liked your product",
        from_user: { id: 2, username: "alice_smith" },
        to_user: { id: 1, username: "john_doe" },
        status: "unread",
        created_at: "2024-01-22T10:30:00Z"
      },
      {
        id: 2,
        message: "bob_wilson commented on your product",
        from_user: { id: 3, username: "bob_wilson" },
        to_user: { id: 1, username: "john_doe" },
        status: "unread",
        created_at: "2024-01-22T09:15:00Z"
      },
      {
        id: 3,
        message: "john_doe bought your product",
        from_user: { id: 1, username: "john_doe" },
        to_user: { id: 2, username: "alice_smith" },
        status: "read",
        created_at: "2024-01-21T14:45:00Z"
      },
      {
        id: 4,
        message: "alice_smith liked your product",
        from_user: { id: 2, username: "alice_smith" },
        to_user: { id: 3, username: "bob_wilson" },
        status: "read",
        created_at: "2024-01-21T11:20:00Z"
      },
      {
        id: 5,
        message: "bob_wilson commented on your product",
        from_user: { id: 3, username: "bob_wilson" },
        to_user: { id: 1, username: "john_doe" },
        status: "read",
        created_at: "2024-01-20T16:30:00Z"
      }
    ];

  const loadNotifications = async () => {
    try {
    //   const res = await api.get(`notifications/`);
    //   setNotifications(res.data);
    setNotifications(dummyNotifications);
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