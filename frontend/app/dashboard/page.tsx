"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { PurchaseOrder, User } from '@/lib/types';

export default function Dashboard() {
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const userRes = await api.get('/auth/me');
        setUser(userRes.data);
        const posRes = await api.get('/pos');
        setPos(posRes.data);
      } catch (err) {
        console.error("Failed to load data", err);
        router.push('/');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [router]);

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout');
      router.push('/');
    } catch (err) {
      console.error(err);
    }
  };


  const getStatusClass = (status: string) => {
    if (status === 'DRAFT') return 'status-draft';
    if (status === 'APPROVED') return 'status-approved';
    if (status === 'NEEDS_REWORK') return 'status-rework';
    if (status === 'INVOICED') return 'status-invoiced';
    return 'status-pending';
  };

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading dashboard...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Dashboard</h1>
          <p className="dashboard-subtitle">
            Welcome, <strong>{user?.email}</strong> (Role: <span className="role-badge">{user?.role}</span>)
          </p>
        </div>
        <div className="button-group">
          <button onClick={() => router.push('/dashboard/create')} className="btn-create">
            + Create New PO
          </button>
          <button onClick={handleLogout} className="btn-danger">
            Logout
          </button>
        </div>
      </div>

      <div className="table-card">
        <table className="po-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Category</th>
              <th>Total Amount</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {pos.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
                  No Purchase Orders found in the system.
                </td>
              </tr>
            ) : (
              pos.map((po) => (
                <tr key={po.id}>
                  <td><strong>#{po.id}</strong></td>
                  <td style={{ fontWeight: '500' }}>{po.title}</td>
                  <td>{po.category}</td>
                  <td style={{ fontWeight: '700' }}>{po.total_amount} {po.currency}</td>
                  <td>
                    <span className={`status-badge ${getStatusClass(po.status)}`}>
                      {po.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>
                    <button 
                      onClick={() => router.push(`/dashboard/${po.id}`)}
                      className="btn-view"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}