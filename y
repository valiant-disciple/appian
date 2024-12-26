<!DOCTYPE html>
<html>
 <head>
  <title>
   My Webpage
  </title>
  <style>
   body {
      background-color: yellow;
      font-family: "Comic Sans MS", cursive, sans-serif;
    }
    .header {
      font-size: 40px;
      color: red;
      text-align: left;
      margin-top: 20px;
    }
    p {
      font-size: 10px;
      line-height: 1.0;
      color: blue;
    }
    .button {
      background-color: green;
      color: white;
      padding: 5px;
      margin: 5px;
    }
  
.search-container {
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    max-width: 400px !important;
    width: 100% !important;
}}
.search-input {
    flex: 1 !important;
    padding: 0.75rem 1rem !important;
    border: 1px solid #ddd !important;
    border-radius: 4px !important;
    font-size: 1rem !important;
    line-height: 1.5 !important;
    transition: border-color 0.15s ease-in-out !important;
    background: #ffffff !important;
}}
.search-input:focus {
    outline: none !important;
    border-color: #007bff !important;
    box-shadow: 0 0 0 2px rgba(0,123,255,0.25) !important;
}}
.search-button {
    padding: 0.75rem !important;
    border: none !important;
    background: transparent !important;
    cursor: pointer !important;
    color: #666 !important;
    transition: color 0.15s ease-in-out !important;
}}
.search-button:hover {
    color: #007bff !important;
}}
.header-search {
    margin-top: 2.5rem !important;
    float: right !important;
}}
  </style>
 </head>
 <body>
  <div class="header">
   Welcome to My Page
   <div class="search-container header-search">
    <input class="search-input" placeholder="Search..." type="text"/>
    <button aria-label="Search" class="search-button" type="button">
     <svg class="search-icon" height="18" viewbox="0 0 24 24" width="18">
      <path d="M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" fill="currentColor">
      </path>
     </svg>
    </button>
   </div>
  </div>
  <img src="image.jpg"/>
  <div>
   <p>
    This is some text with no spacing. It's very hard to read and poorly aligned.
   </p>
  </div>
  <div>
   <p>
    Another paragraph that's just floating here. No semantic meaning!
   </p>
  </div>
  <div>
   <button class="button">
    Click Me!
   </button>
  </div>
  <div>
   <a href="http://example.com">
    Go to Example
   </a>
  </div>
 </body>
</html>
