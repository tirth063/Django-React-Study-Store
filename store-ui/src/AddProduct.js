import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from "./api";
function AddProduct() {
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const [price, setPrice] = useState('');
  const [image, setImage] = useState(null);
  const [nameError, setNameError] = useState('');
  const [descError, setDescError] = useState('');
  const [priceError, setPriceError] = useState('');
  const [imageError, setImageError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setNameError('');
    setDescError('');
    setPriceError('');
    setImageError('');

    const formData = new FormData();
    formData.append('name', name);
    formData.append('desc', desc);
    formData.append('price', price);
    formData.append('image', image);

    try {
      await api.post(`products/create/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      navigate('/');
    } catch (err) {
      const errors = err.response?.data;
      if (errors?.name) setNameError(errors.name[0]);
      if (errors?.desc) setDescError(errors.desc[0]);
      if (errors?.price) setPriceError(errors.price[0]);
      if (errors?.image) setImageError(errors.image[0]);
    }
  };

  return (
    <div className="container mt-4">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow">
            <div className="card-body p-4">
              <h3 className="mb-4">Add New Product</h3>
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label className="form-label">Product Name</label>
                  <input
                    type="text"
                    className="form-control"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                  />
                  {nameError && <small className="text-danger">{nameError}</small>}
                </div>
                <div className="mb-3">
                  <label className="form-label">Description</label>
                  <textarea
                    className="form-control"
                    rows="4"
                    value={desc}
                    onChange={(e) => setDesc(e.target.value)}
                    required
                  ></textarea>
                  {descError && <small className="text-danger">{descError}</small>}
                </div>
                <div className="mb-3">
                  <label className="form-label">Price</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-control"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    required
                  />
                  {priceError && <small className="text-danger">{priceError}</small>}
                </div>
                <div className="mb-3">
                  <label className="form-label">Image</label>
                  <input
                    type="file"
                    className="form-control"
                    accept="image/*"
                    onChange={(e) => setImage(e.target.files[0])}
                    required
                  />
                  {imageError && <small className="text-danger">{imageError}</small>}
                </div>
                <button type="submit" className="btn btn-primary w-100">Add Product</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AddProduct;