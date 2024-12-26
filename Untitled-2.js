// Global state management
var currentTheme = 'light'
var isMenuOpen = false
var cartItems = []
var userData = null
var notifications = []

// Directly manipulating styles
function toggleTheme() {
    if(currentTheme === 'light') {
        document.body.style.backgroundColor = '#333'
        document.body.style.color = '#fff'
        var allDivs = document.getElementsByTagName('div')
        for(var i = 0; i < allDivs.length; i++) {
            allDivs[i].style.borderColor = '#fff'
        }
        currentTheme = 'dark'
    } else {
        document.body.style.backgroundColor = '#fff'
        document.body.style.color = '#333'
        var allDivs = document.getElementsByTagName('div')
        for(var i = 0; i < allDivs.length; i++) {
            allDivs[i].style.borderColor = '#333'
        }
        currentTheme = 'light'
    }
}

// Bad modal implementation
function showModal(message) {
    var modal = document.createElement('div')
    modal.style.position = 'fixed'
    modal.style.top = '50%'
    modal.style.left = '50%'
    modal.style.transform = 'translate(-50%, -50%)'
    modal.style.backgroundColor = '#fff'
    modal.style.padding = '20px'
    modal.style.border = '2px solid #333'
    modal.style.zIndex = '1000'
    modal.innerHTML = message + '<br><button onclick="this.parentElement.remove()">Close</button>'
    document.body.appendChild(modal)
}

// Poor notification system
function addNotification(text) {
    notifications.push(text)
    var notifDiv = document.createElement('div')
    notifDiv.style.position = 'fixed'
    notifDiv.style.top = (notifications.length * 60) + 'px'
    notifDiv.style.right = '20px'
    notifDiv.style.backgroundColor = 'yellow'
    notifDiv.style.padding = '10px'
    notifDiv.style.border = '1px solid black'
    notifDiv.innerHTML = text
    document.body.appendChild(notifDiv)
    setTimeout(function() {
        notifDiv.remove()
        notifications.shift()
    }, 3000)
}

// Bad menu toggle
function toggleMenu() {
    var menu = document.getElementById('menu')
    if(isMenuOpen) {
        menu.style.left = '-200px'
        isMenuOpen = false
    } else {
        menu.style.left = '0px'
        isMenuOpen = true
    }
}

// Directly creating UI elements
function createProductCard(product) {
    return `
        <div style="border: 1px solid #ccc; padding: 10px; margin: 10px; width: 200px; display: inline-block;">
            <img src="${product.image}" style="width: 100%; height: 150px; object-fit: cover;">
            <h3 style="margin: 5px 0; color: blue;">${product.name}</h3>
            <p style="color: green;">$${product.price}</p>
            <button onclick="addToCart('${product.id}')">Add to Cart</button>
        </div>
    `
}

// Bad cart management
function addToCart(productId) {
    cartItems.push(productId)
    updateCart()
    addNotification('Added to cart!')
}

function updateCart() {
    var cart = document.getElementById('cart')
    cart.innerHTML = ''
    cart.style.position = 'fixed'
    cart.style.right = '0'
    cart.style.top = '0'
    cart.style.width = '300px'
    cart.style.height = '100%'
    cart.style.backgroundColor = '#f0f0f0'
    cart.style.padding = '20px'
    cart.style.overflowY = 'auto'
    
    cartItems.forEach(function(item) {
        cart.innerHTML += `<div style="border-bottom: 1px solid #ccc; padding: 10px;">
            Item: ${item}
            <button onclick="removeFromCart('${item}')" style="color: red;">Remove</button>
        </div>`
    })
}

// Bad form validation
function validateForm() {
    var name = document.getElementById('name').value
    var email = document.getElementById('email').value
    var phone = document.getElementById('phone').value
    
    if(name.length < 2) {
        showModal('Name too short!')
        return false
    }
    
    if(!email.includes('@')) {
        showModal('Invalid email!')
        return false
    }
    
    if(phone.length != 10) {
        showModal('Phone must be 10 digits!')
        return false
    }
    
    userData = {name, email, phone}
    showModal('Success!')
    return true
}

// Bad initialization
window.onload = function() {
    document.body.innerHTML += `
        <div id="menu" style="position: fixed; left: -200px; top: 0; width: 200px; height: 100%; 
             background-color: #f0f0f0; transition: left 0.3s; padding: 20px;">
            <button onclick="toggleMenu()">Toggle Menu</button>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 10px 0;"><a href="#" style="color: blue; text-decoration: none;">Home</a></li>
                <li style="margin: 10px 0;"><a href="#" style="color: blue; text-decoration: none;">Products</a></li>
                <li style="margin: 10px 0;"><a href="#" style="color: blue; text-decoration: none;">Contact</a></li>
            </ul>
        </div>
        
        <div id="cart"></div>
        
        <form onsubmit="return validateForm()" style="margin: 20px;">
            <input type="text" id="name" placeholder="Name" style="margin: 5px;"><br>
            <input type="email" id="email" placeholder="Email" style="margin: 5px;"><br>
            <input type="tel" id="phone" placeholder="Phone" style="margin: 5px;"><br>
            <button type="submit" style="margin: 5px;">Submit</button>
        </form>
        
        <button onclick="toggleTheme()" style="position: fixed; bottom: 20px; right: 20px;">
            Toggle Theme
        </button>
    `
    
    // Add some sample products
    var products = [
        {id: 'p1', name: 'Product 1', price: 99.99, image: 'product1.jpg'},
        {id: 'p2', name: 'Product 2', price: 149.99, image: 'product2.jpg'},
        {id: 'p3', name: 'Product 3', price: 199.99, image: 'product3.jpg'}
    ]
    
    var productContainer = document.createElement('div')
    productContainer.style.margin = '20px'
    productContainer.innerHTML = products.map(createProductCard).join('')
    document.body.appendChild(productContainer)
}