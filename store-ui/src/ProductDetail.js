import { Cookies } from 'react-cookie';
import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from './api';
import { Modal, Button } from 'react-bootstrap';
function ProductDetail() {
  const cookies = new Cookies();
  const { id } = useParams();
  const [product, setProduct] = useState(null);
  const [comment, setComment] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  // const user = cookies.get('user');
  const user = {id:1,username:"tirth",email:"tirth@gmail.com",balance:10000};
  const navigate = useNavigate();

  useEffect(() => {
    loadProduct();
  }, [id]);

  const dummyProducts = [
      {
        id: 1,
        name: "Wireless Headphones",
        desc: "High-quality wireless headphones with noise cancellation and 30-hour battery life. Perfect for music lovers and professionals.",
        price: "149.99",
        image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
        user: { id: 1, username: "john_doe" },
        like_count: 15,
        comment_count: 8,
        is_liked_by_user: false,
        is_owner: false,
        created_at: "2024-01-20T10:30:00Z",
        comments: [
          {
            id: 1,
            content: "Great product! Sound quality is amazing.",
            user: { id: 2, username: "alice_smith" },
            created_at: "2024-01-21T14:20:00Z"
          },
          {
            id: 2,
            content: "Worth every penny. Highly recommend!",
            user: { id: 3, username: "bob_wilson" },
            created_at: "2024-01-21T16:45:00Z"
          }
        ]
      },
      {
        id: 2,
        name: "Smart Watch",
        desc: "Feature-rich smartwatch with fitness tracking, heart rate monitor, and smartphone notifications. Water resistant up to 50 meters.",
        price: "299.99",
        image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
        user: { id: 2, username: "alice_smith" },
        like_count: 23,
        comment_count: 12,
        is_liked_by_user: true,
        is_owner: false,
        created_at: "2024-01-19T09:15:00Z",
        comments: [
          {
            id: 3,
            content: "Perfect for my daily workouts!",
            user: { id: 1, username: "john_doe" },
            created_at: "2024-01-20T08:30:00Z"
          }
        ]
      },
      {
        id: 3,
        name: "Laptop Stand",
        desc: "Ergonomic aluminum laptop stand with adjustable height and angle. Improves posture and reduces neck strain during long work sessions.",
        price: "49.99",
        image: "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
        user: { id: 3, username: "bob_wilson" },
        like_count: 8,
        comment_count: 5,
        is_liked_by_user: false,
        is_owner: false,
        created_at: "2024-01-18T15:45:00Z",
        comments: []
      },
      {
        id: 4,
        name: "Mechanical Keyboard",
        desc: "RGB backlit mechanical keyboard with blue switches. Perfect for gaming and typing. Features programmable keys and anti-ghosting.",
        price: "129.99",
        image: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400",
        user: { id: 1, username: "john_doe" },
        like_count: 31,
        comment_count: 15,
        is_liked_by_user: true,
        is_owner: false,
        created_at: "2024-01-17T11:20:00Z",
        comments: [
          {
            id: 4,
            content: "Best keyboard I've ever used!",
            user: { id: 2, username: "alice_smith" },
            created_at: "2024-01-18T09:10:00Z"
          },
          {
            id: 5,
            content: "The RGB lighting is fantastic.",
            user: { id: 3, username: "bob_wilson" },
            created_at: "2024-01-18T12:30:00Z"
          }
        ]
      },
      {
        id: 5,
        name: "Wireless Mouse",
        desc: "Precision wireless mouse with ergonomic design. Features 6 programmable buttons and long-lasting rechargeable battery.",
        price: "39.99",
        image: "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400",
        user: { id: 2, username: "alice_smith" },
        like_count: 12,
        comment_count: 6,
        is_liked_by_user: false,
        is_owner: false,
        created_at: "2024-01-16T13:00:00Z",
        comments: [
          {
            id: 6,
            content: "Very comfortable for long use.",
            user: { id: 1, username: "john_doe" },
            created_at: "2024-01-17T10:15:00Z"
          }
        ]
      },
      {
        id: 6,
        name: "USB-C Hub",
        desc: "7-in-1 USB-C hub with HDMI, USB 3.0 ports, SD card reader, and power delivery. Essential accessory for modern laptops.",
        price: "59.99",
        image: "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=400",
        user: { id: 3, username: "bob_wilson" },
        like_count: 19,
        comment_count: 9,
        is_liked_by_user: true,
        is_owner: false,
        created_at: "2024-01-15T16:30:00Z",
        comments: []
      }
    ];

  const loadProduct = async () => {
    try {
      // const res = await api.get(`products/public/`);
      // const found = res.data.find(p => p.id === parseInt(id));
      const found = dummyProducts.find(p => p.id === parseInt(id));
      setProduct(found);
    } catch (err) {
      console.error(err);
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!user) {
      setModalType('comment');
      setShowModal(true);
      return;
    }
    try {
      await api.post(`products/${id}/comment/`, { content: comment });
      setComment('');
      loadProduct();
    } catch (err) {
      console.error(err);
    }
  };

  const handleBuy = async () => {
    if (!user) {
      setModalType('buy');
      setShowModal(true);
      return;
    }
    try {
      await api.post(`products/${id}/buy/`);
      alert('Product purchased successfully!');
      navigate('/');
    } catch (err) {
      alert(err.response?.data?.error || 'Purchase failed');
    }
  };

  if (!product) return <div className="container mt-5">Loading...</div>;

  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-md-6">
          <img
            src={product.image}
            className="img-fluid rounded"
            alt={product.name}
          />
        </div>
        <div className="col-md-6">
          <h2>{product.name}</h2>
          <p className="text-muted">By {product.user.username}</p>
          <h4 className="text-success">${product.price}</h4>
          <p className="mt-3">{product.desc}</p>
          <button className="btn btn-success btn-lg" onClick={handleBuy}>
            <i className="bi bi-cart"></i> Buy Now
          </button>
        </div>
      </div>

      <div className="mt-5">
        <h4>Comments ({product.comment_count})</h4>
        <form onSubmit={handleComment} className="mb-4">
          <textarea
            className="form-control mb-2"
            rows="3"
            placeholder="Add a comment..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            required
          ></textarea>
          <button type="submit" className="btn btn-primary">Post Comment</button>
        </form>

        {product.comments.map(c => (
          <div key={c.id} className="card mb-3">
            <div className="card-body">
              <h6 className="card-subtitle mb-2">{c.user.username}</h6>
              <p className="card-text">{c.content}</p>
              <small className="text-muted">{new Date(c.created_at).toLocaleString()}</small>
            </div>
          </div>
        ))}
      </div>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Login Required</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Please login to {modalType === 'buy' ? 'buy products' : 'add comments'}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>Close</Button>
          <Link to="/login" className="btn btn-primary">Login</Link>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default ProductDetail;