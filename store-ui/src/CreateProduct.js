import { useState } from "react";
import api from "./api";
import { useNavigate } from "react-router-dom";

function CreateProduct() {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [image, setImage] = useState(null);
  const navigate = useNavigate();

  const create = async () => {
    const form = new FormData();
    form.append("name", name);
    form.append("price", price);
    form.append("image", image);

    await api.post("products/create/", form);
    alert("Product created");
    navigate("/");
  };

  return (
    <div>
      <h2>Create Product</h2>

      <input placeholder="name" onChange={e => setName(e.target.value)} />
      <br />
      <input placeholder="price" onChange={e => setPrice(e.target.value)} />
      <br />
      <input type="file" onChange={e => setImage(e.target.files[0])} />
      <br />

      <button onClick={create}>Create</button>
    </div>
  );
}

export default CreateProduct;