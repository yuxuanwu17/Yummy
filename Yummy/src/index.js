import React from 'react';
import ReactDOM from 'react-dom';
import Cart from './Cart';

document.addEventListener('DOMContentLoaded', () => {
  const cartElement = document.getElementById('cart');
  if (cartElement) {
    ReactDOM.render(<Cart />, cartElement);
  }
});
