import React, { useState, useEffect } from 'react';
import { Link} from 'react-router-dom';
import { Cookies } from 'react-cookie';
import api from './api';
import { Modal, Button } from 'react-bootstrap';
function Home() {
  const cookies = new Cookies();
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const user = cookies.get('user');

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const res = await api.get(`products/public/`);
      setProducts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLike = async (productId) => {
    if (!user) {
      setShowModal(true);
      return;
    }
    try {
      await api.post(`products/${productId}/like/`);
      loadProducts();
    } catch (err) {
      console.error(err);
    }
  };

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.user.username.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Products</h2>
      <input
        type="text"
        className="form-control mb-4"
        placeholder="Search by product or username..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      
      <div className="row g-4">
        {filtered.map(product => (
          <div key={product.id} className="col-md-4">
            <div className="card h-100 shadow-sm">
              <img
                src={product.image}
                className="card-img-top"
                style={{ height: '200px', objectFit: 'cover' }}
                alt={product.name}
              />
              <div className="card-body">
                <h5 className="card-title">{product.name}</h5>
                <p className="text-muted mb-2">
                  <i className="bi bi-person"></i> {product.user.username}
                </p>
                <p className="card-text">{product.desc.substring(0, 100)}...</p>
                <h6 className="text-success">${product.price}</h6>
                <div className="d-flex justify-content-between align-items-center">
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleLike(product.id)}
                  >
                    <i className={`bi bi-heart${product.is_liked_by_user ? '-fill' : ''}`}></i> {product.like_count}
                  </button>
                  <Link to={`/product/${product.id}`} className="btn btn-sm btn-primary">
                    View Details
                  </Link>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Login Required</Modal.Title>
        </Modal.Header>
        <Modal.Body>Please login to like products</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>Close</Button>
          <Link to="/login" className="btn btn-primary">Login</Link>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default Home;