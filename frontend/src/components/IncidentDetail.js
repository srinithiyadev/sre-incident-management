import React, { useEffect, useState } from 'react';
import { getWorkitem, updateStatus } from '../api';
import RCAForm from './RCAForm';

const NEXT_STATUS = {
  OPEN:          'INVESTIGATING',
  INVESTIGATING: 'RESOLVED',
  RESOLVED:      'CLOSED',
  CLOSED:        null,
};

export default function IncidentDetail({ id, onBack }) {
  const [data,       setData]       = useState(null);
  const [loading,    setLoading]    = useState(true);
  const [showRCA,    setShowRCA]    = useState(false);
  const [updating,   setUpdating]   = useState(false);

  const load = async () => {
    try {
      const res = await getWorkitem(id);
      setData(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const handleStatusUpdate = async () => {
    const next = NEXT_STATUS[data.workitem.status];
    if (!next) return;

    if (next === 'CLOSED' && !showRCA) {
      setShowRCA(true);
      return;
    }

    setUpdating(true);
    try {
      await updateStatus(id, next);
      await load();
    } catch (e) {
      alert(e.response?.data?.detail || e.message);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) return <p style={{color:'#718096'}}>Loading...</p>;
  if (!data)   return <p style={{color:'#fc8181'}}>Not found</p>;

  const { workitem, signals } = data;
  const nextStatus = NEXT_STATUS[workitem.status];

  return (
    <div>
      <button className="back-btn" onClick={onBack}>← Back to incidents</button>

      <div className="card" style={{cursor:'default'}}>
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
          <h3>{workitem.title}</h3>
          <span className={`badge ${workitem.priority}`}>{workitem.priority}</span>
        </div>
        <div className="card-meta">
          <span className={`badge ${workitem.status}`}>{workitem.status}</span>
          <span>Component: {workitem.component_id}</span>
          <span>Signals: {workitem.signal_count}</span>
          {workitem.mttr_minutes && <span>MTTR: {workitem.mttr_minutes.toFixed(1)} min</span>}
        </div>

        <div style={{marginTop:'1rem', display:'flex', gap:'0.5rem'}}>
          {nextStatus && (
            <button
              className="btn-primary"
              onClick={handleStatusUpdate}
              disabled={updating}
            >
              {updating ? 'Updating...' : `Move to ${nextStatus}`}
            </button>
          )}
          {workitem.status === 'RESOLVED' && (
            <button className="btn-warning" onClick={() => setShowRCA(!showRCA)}>
              {showRCA ? 'Hide RCA Form' : 'Submit RCA'}
            </button>
          )}
        </div>
      </div>

      {showRCA && (
        <RCAForm
          workitemId={id}
          onSubmitted={() => { setShowRCA(false); load(); }}
        />
      )}

      <p className="section-title">📡 Raw Signals ({signals.length})</p>
      <div className="signals-list">
        {signals.length === 0 && <p style={{color:'#718096'}}>No signals found</p>}
        {signals.map((s, i) => (
          <div key={i} className="signal-item">
            <strong>{s.component_id}</strong> — {s.error_message}
            <span style={{float:'right'}}>{new Date(s.timestamp).toLocaleTimeString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}