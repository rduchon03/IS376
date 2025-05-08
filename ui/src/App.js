import React, { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/books')
      .then(res => setBooks(res.data))
      .catch(err => console.error('Error fetching books:', err));
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h1>Book List</h1>
      {books.length === 0 ? (
        <p>Loading...</p>
      ) : (
        <ul>
          {books.map((book, index) => (
            <li key={index}>
              <strong>{book.name}</strong> by {book.author} (ISBN: {book.isbn}) - {book.genre}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
