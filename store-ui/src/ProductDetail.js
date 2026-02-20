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
  const user = cookies.get('user');
  const navigate = useNavigate();

  useEffect(() => {
    loadProduct();
  }, [id]);

  const loadProduct = async () => {
    try {
      const res = await api.get(`products/${id}/`);
      setProduct(res.data);
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