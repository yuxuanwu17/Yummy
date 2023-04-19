import React, { useState, useEffect } from 'react';

const Cart = () => {
  console.log('Cart rendered');
  const [foods, setFoods] = useState([]);

  const fetchData = () => {
    fetch('/yummy/api/order/')
      .then((response) => response.json())
      .then((data) => {
        if (data.length > 0) {
          setFoods(data[0].foods);
        } else {
          setFoods([]);
        }
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    const handleCartChanged = () => {
      fetchData();
    };

    document.addEventListener('cartChanged', handleCartChanged);
    return () => {
      document.removeEventListener('cartChanged', handleCartChanged);
    };
  }, []);

  return (
    <div className="cart">
      <ul>
        {foods.map((foodSet) => (
          <div key={foodSet.id}>
            {foodSet.food.name} - ${foodSet.food.price} x {foodSet.quantity}
          </div>
        ))}
      </ul>
    </div>
  );
};

export default Cart;
