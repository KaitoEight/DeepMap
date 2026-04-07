# Frontend Integration Guide

## Cấu hình API Base URL

Tạo file `src/api/client.js`:

```javascript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const apiClient = {
  async get(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    return response.json();
  },

  async post(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async put(endpoint, data) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async delete(endpoint) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
    });
    return response.json();
  },
};
```

## Cập nhật SearchPage.jsx

```javascript
import { useState, useMemo, useEffect } from "react";
import { apiClient } from '../api/client';

export default function SearchPage() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchListings();
  }, []);

  const fetchListings = async (filters = {}) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.type) params.append('type', filters.type);
      if (filters.maxPrice) params.append('max_price', filters.maxPrice);
      if (filters.maxDistance) params.append('max_distance', filters.maxDistance);
      if (filters.sortBy) params.append('sort_by', filters.sortBy);
      
      const data = await apiClient.get(`/listings?${params}`);
      setListings(data);
    } catch (error) {
      console.error('Error fetching listings:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSave = async (id) => {
    const userId = localStorage.getItem('userId') || 'guest';
    try {
      const listing = listings.find(l => l.id === id);
      if (listing.isSaved) {
        await apiClient.delete(`/favorites/${id}/${userId}`);
      } else {
        await apiClient.post('/favorites', {
          listing_id: id,
          user_id: userId,
        });
      }
      setListings(prev =>
        prev.map(l => (l.id === id ? { ...l, isSaved: !l.isSaved } : l))
      );
    } catch (error) {
      console.error('Error toggling save:', error);
    }
  };

  // ... rest of component
}
```

## Environment Variables

Tạo `.env` tại root của frontend project:

```
VITE_API_URL=http://localhost:8000/api
```

## Common API Calls

### Fetch listings with filters
```javascript
const data = await apiClient.get('/listings?type=Phòng%20trọ&max_price=5&sort_by=ai');
```

### Add to favorites
```javascript
await apiClient.post('/favorites', {
  listing_id: 1,
  user_id: 'user@example.com',
});
```

### Check if favorited
```javascript
const result = await apiClient.get('/favorites/1/user@example.com');
console.log(result.is_favorited);
```

### Create review
```javascript
await apiClient.post('/reviews', {
  listing_id: 1,
  user_id: 'user@example.com',
  rating: 5,
  comment: 'Phòng rất tốt!',
});
```

### Get listing details
```javascript
const listing = await apiClient.get('/listings/1');
console.log(listing.reviews, listing.favorites);
```
