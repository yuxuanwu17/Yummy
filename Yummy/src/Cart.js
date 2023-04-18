import React, { useState, useEffect } from 'react';

const Cart = () => {
  console.log('Cart rendered')
  const [foods, setFoods] = useState([]);

  useEffect(() => {
    fetch('yummy/api/order/')
      .then((response) => response.json())
      .then((data) => {
        if (data.length > 0) {
          setFoods(data[0].foods);
        } else {
          setFoods([]);
        }
      });
  }, []);

  return (
    <div className="cart">
      <h2>Cart</h2>
      <ul>
        {foods.map((foodSet) => (
          <li key={foodSet.id}>
            {foodSet.food.name} - ${foodSet.food.price} x {foodSet.quantity}
          </li>
        ))}
      </ul>
      <h3>
        Total: $
        {foods.reduce((total, foodSet) => total + foodSet.food.price * foodSet.quantity, 0)}
      </h3>
    </div>
  );
};

export default Cart;
