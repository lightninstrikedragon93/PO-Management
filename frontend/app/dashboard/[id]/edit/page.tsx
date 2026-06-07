"use client";

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import api from '@/lib/api';
import { POCategoryEnum } from '@/lib/types';

export default function EditPO() {
  const params = useParams();
  const router = useRouter();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<POCategoryEnum>('Services');
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPO = async () => {
      try {
        const res = await api.get(`/pos/${params.id}`);
        const po = res.data;
        
        if (po.status !== 'DRAFT' && po.status !== 'NEEDS_REWORK') {
          router.push(`/dashboard/${po.id}`);
          return;
        }

        setTitle(po.title);
        setDescription(po.description || '');
        setCategory(po.category);
        setItems(po.items.length > 0 ? po.items : [{ name: '', quantity: 1, unit_price: 0 }]);
      } catch (err) {
        setError('Failed to load PO details');
      } finally {
        setLoading(false);
      }
    };
    fetchPO();
  }, [params.id, router]);

  const liveTotal = items.reduce((sum, item) => sum + (Number(item.quantity || 0) * Number(item.unit_price || 0)), 0);

  const handleAddItem = () => setItems([...items, { name: '', quantity: 1, unit_price: 0 }]);
  
  const handleItemChange = (index: number, field: string, value: any) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length > 1) setItems(items.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.put(`/pos/${params.id}`, {
        title,
        description,
        category,
        currency: 'USD',
        items: items.map(item => ({
          name: item.name,
          quantity: Number(item.quantity),
          unit_price: Number(item.unit_price)
        }))
      });
      router.push(`/dashboard/${params.id}`); 
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update PO");
    }
  };

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading PO for edit...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Edit PO #{params.id}</h1>
        <button onClick={() => router.push(`/dashboard/${params.id}`)} className="btn-secondary">Cancel</button>
      </div>

      <div className="form-card">
        {error && <div style={{ color: 'red', marginBottom: '1rem', fontWeight: 'bold' }}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-col">
              <label className="form-label">Title</label>
              <input type="text" className="form-input" value={title} onChange={e => setTitle(e.target.value)} required />
            </div>
            <div className="form-col">
              <label className="form-label">Category</label>
              <select className="form-input" value={category} onChange={e => setCategory(e.target.value as POCategoryEnum)}>
                <option value="Services">Services</option>
                <option value="Office Supplies">Office Supplies</option>
                <option value="IT Equipment">IT Equipment</option>
              </select>
            </div>
          </div>
          
          <div className="form-group" style={{ marginBottom: '1.5rem' }}>
            <label className="form-label">Description</label>
            <textarea className="form-input" rows={2} value={description} onChange={e => setDescription(e.target.value)} />
          </div>

          <div className="items-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontWeight: 600 }}>Line Items</h3>
              <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--primary-color)' }}>
                Live Total: ${liveTotal.toFixed(2)}
              </div>
            </div>

            {items.map((item, index) => (
              <div key={index} className="item-row">
                <div style={{ flex: 2 }}>
                  <label className="form-label">Item Name</label>
                  <input type="text" className="form-input" value={item.name} onChange={e => handleItemChange(index, 'name', e.target.value)} required />
                </div>
                <div style={{ flex: 1 }}>
                  <label className="form-label">Quantity</label>
                  <input type="number" min="1" className="form-input" value={item.quantity} onChange={e => handleItemChange(index, 'quantity', e.target.value)} required />
                </div>
                <div style={{ flex: 1 }}>
                  <label className="form-label">Unit Price ($)</label>
                  <input type="number" min="0.01" step="0.01" className="form-input" value={item.unit_price} onChange={e => handleItemChange(index, 'unit_price', e.target.value)} required />
                </div>
                <button type="button" className="btn-danger" onClick={() => handleRemoveItem(index)} style={{ padding: '0.5rem 1rem' }}>X</button>
              </div>
            ))}
            <button type="button" className="btn-secondary" onClick={handleAddItem}>+ Add Another Item</button>
          </div>

          <button type="submit" className="btn-create" style={{ width: '100%', marginTop: '2rem' }}>Save Changes</button>
        </form>
      </div>
    </div>
  );
}