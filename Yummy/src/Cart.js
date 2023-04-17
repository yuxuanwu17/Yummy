import React, { useState, useEffect } from 'react';

const Cart = () => {
  const [cartItems, setCartItems] = useState([]);

  useEffect(() => {
    fetchOrder();
  }, []);

  const fetchOrder = async () => {
    const response = await fetch('/api/order/1/'); // Replace 1 with the order ID you want to fetch
    const data = await response.json();
    setCartItems(data.foods);
  };

  const getTotalPrice = () => {
    return cartItems.reduce(
      (total, item) => total + item.food.price * item.quantity,
      0
    );
  };

  return (
    <div className="cart">
      <div className="cart-floating-window">
        <h3>Shopping Cart</h3>
        <ul>
          {cartItems.map((item) => (
            <li key={item.id}>
              {item.food.name} x{item.quantity} - ${item.food.price * item.quantity}
            </li>
          ))}
        </ul>
        <p>Total: ${getTotalPrice().toFixed(2)}</p>
      </div>
    </div>
  );
};

export default Cart;
