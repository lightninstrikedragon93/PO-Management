"use client";

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import api from '@/lib/api';

export default function PODetails() {
  const params = useParams();
  const router = useRouter();
  const [po, setPo] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDetails = async () => {
    try {
      const [userRes, poRes] = await Promise.all([
        api.get('/auth/me'),
        api.get(`/pos/${params.id}`)
      ]);
      setUser(userRes.data);
      setPo(poRes.data);
    } catch (err) {
      router.push('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [params.id]);

  const handleAction = async (action: 'submit' | 'approve' | 'reject' | 'invoice') => {
    if (action === 'reject') {
      const isConfirmed = window.confirm("Esti sigur ca vrei sa respingi aceasta cerere?");
      if (!isConfirmed) return;
    }

    try {
      setError('');
      if (action === 'reject' && !comment) {
        setError('You must provide a reason for rejection.');
        return;
      }

      const payload = action === 'approve' ? { comment } : action === 'reject' ? { reason: comment } : {};
      await api.post(`/pos/${params.id}/${action}`, payload);
      
      setComment('');
      fetchDetails(); 
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to ${action} PO`);
    }
  };

  if (loading || !po) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading details...</div>;


  const isCreator = user?.id === po.creator_id;
  const canSubmit = (po.status === 'DRAFT' || po.status === 'NEEDS_REWORK') && isCreator;
  const canApproveManager = po.status === 'PENDING_MANAGER' && user?.role === 'manager';
  const canApproveIT = po.status === 'PENDING_IT' && user?.role === 'it_rep';
  const canApproveFinance = po.status === 'PENDING_FINANCE' && user?.role === 'finance';
  const canInvoice = po.status === 'APPROVED' && user?.role === 'finance';
  
  const needsReviewAction = canApproveManager || canApproveIT || canApproveFinance;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">PO #{po.id}: {po.title}</h1>
          <span className={`status-badge ${po.status === 'DRAFT' ? 'status-draft' : po.status === 'APPROVED' ? 'status-approved' : 'status-pending'}`}>
            {po.status}
          </span>
        </div>
        <button onClick={() => router.push('/dashboard')} className="btn-secondary">Back to Dashboard</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="details-grid">
        <div>
          <div className="form-card info-section">
            <h3 style={{ fontSize: '1.2rem', marginBottom: '1.5rem', borderBottom: '1px solid #e5e7eb', paddingBottom: '0.5rem' }}>General Information</h3>
            <div className="form-row">
              <div className="form-col">
                <div className="info-label">Category</div>
                <div className="info-value">{po.category}</div>
              </div>
              <div className="form-col">
                <div className="info-label">Total Amount</div>
                <div className="info-value" style={{ color: 'var(--primary-color)', fontSize: '1.5rem' }}>
                  {po.total_amount} {po.currency}
                </div>
              </div>
            </div>
            <div className="info-label">Description</div>
            <div className="info-value">{po.description || "No description provided."}</div>
          </div>

          <div className="form-card">
            <h3 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>Line Items</h3>
            <table className="po-table">
              <thead><tr><th>Name</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr></thead>
              <tbody>
                {po.items?.map((item: any) => (
                  <tr key={item.id}>
                    <td>{item.name}</td><td>{item.quantity}</td><td>${item.unit_price}</td>
                    <td><strong>${item.quantity * item.unit_price}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {(canSubmit || needsReviewAction || canInvoice) && (
            <div className="workflow-actions">
              <h3 style={{ marginBottom: '1rem' }}>Workflow Actions</h3>
              
                            {canSubmit && (
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button onClick={() => handleAction('submit')} className="btn-create" style={{ flex: 2 }}>
                    Submit for Approval
                  </button>
                  <button 
                    onClick={() => router.push(`/dashboard/${po.id}/edit`)} 
                    className="btn-secondary" style={{ flex: 1, textAlign: 'center' }}
                  >
                    Edit PO
                  </button>
                </div>
              )}

              {needsReviewAction && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <textarea 
                    className="form-input" 
                    placeholder="Add a comment or rejection reason..." 
                    value={comment} 
                    onChange={e => setComment(e.target.value)} 
                    rows={2} 
                  />
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <button onClick={() => handleAction('approve')} className="btn-create" style={{ flex: 1 }}>Approve PO</button>
                    <button onClick={() => handleAction('reject')} className="btn-danger" style={{ flex: 1 }}>Reject (Needs Rework)</button>
                  </div>
                </div>
              )}

              {canInvoice && (
                <button onClick={() => handleAction('invoice')} className="btn-create" style={{ width: '100%', backgroundColor: '#1d4ed8' }}>Mark as Invoiced</button>
              )}
            </div>
          )}
        </div>

        <div>
          <div className="form-card">
            <h3 style={{ fontSize: '1.2rem', marginBottom: '1.5rem', borderBottom: '1px solid #e5e7eb', paddingBottom: '0.5rem' }}>Audit Trail</h3>
            {po.audit_logs?.length === 0 ? (
              <p className="info-value">No actions recorded yet.</p>
            ) : (
              <ul className="audit-log-list">
                {po.audit_logs?.map((log: any) => (
                  <li key={log.id} className="audit-log-item">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <strong>{log.action}</strong>
                      <span className="info-label">{new Date(log.created_at).toLocaleString()}</span>
                    </div>
                    <div style={{ fontSize: '0.9rem', color: '#4b5563' }}>
                      Actor: <strong>{log.actor.email}</strong>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#6b7280', margin: '0.25rem 0' }}>
                      {log.from_status} ➔ {log.to_status}
                    </div>
                    {log.comments && (
                      <div style={{ marginTop: '0.5rem', padding: '0.5rem', backgroundColor: '#f3f4f6', borderRadius: '4px', fontStyle: 'italic', fontSize: '0.9rem' }}>
                        "{log.comments}"
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}