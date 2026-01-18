import { useEffect, useState } from "react";
import api from "./api";

function Home() {
  const [products, setProducts] = useState([]);
  const [comment, setComment] = useState("");

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      const res = await api.get("products/");
      console.log("API RESPONSE:", res.data);

      if (Array.isArray(res.data)) {
        setProducts(res.data);
      } else {
        setProducts([]);
      }
    } catch (err) {
      console.error(err);
      setProducts([]);
    }
  };

  const likeProduct = async (id) => {
    await api.post(`like/${id}/`);
    alert("Liked / Unliked");
  };

  const addComment = async (id) => {
    if (!comment.trim()) {
      alert("Comment required");
      return;
    }

    await api.post("comments/", {
      product: id,
      content: comment,
    });

    alert("Comment added");
    setComment("");
  };

  return (
    <div>
      <h2>Products</h2>

      {products.length === 0 && <p>No products found</p>}

      {products.map(p => (
        <div key={p.id}>
          <p>Name: {p.name}</p>
          <p>Price: {p.price}</p>
          <p>Owner: {p.owner}</p>

          <button onClick={() => likeProduct(p.id)}>Like</button>

          <br />

          <input
            placeholder="comment"
            value={comment}
            onChange={e => setComment(e.target.value)}
          />

          <button onClick={() => addComment(p.id)}>Comment</button>

          <hr />
        </div>
      ))}
    </div>
  );
}

export default Home;
