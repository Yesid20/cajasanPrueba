import React, { useEffect, useState } from "react";
import api from "../api";
import { clearTokens, getAccessToken, getRefreshToken } from "../auth";
import { useNavigate } from "react-router-dom";

type Item = {
  id: number;
  name: string;
  category: string;
  price: number;
  stock: number;
};

export default function Products() {
  const [items, setItems] = useState<Item[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const resp = await api.get("/products");
        setItems(resp.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Error fetching products");
      }
    })();
  }, []);

  const handleLogout = async () => {
    try {
      const refresh = getRefreshToken();
      if (refresh) {
        await api.post("/auth/logout", { refresh_token: refresh });
      }
    } finally {
      clearTokens();
      navigate("/login");
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "2rem auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Products</h2>
        <div>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <ul>
        {items.map((it) => (
          <li key={it.id}>
            <strong>{it.name}</strong> — {it.category} — ${it.price} — stock: {it.stock}
          </li>
        ))}
      </ul>
    </div>
  );
}
