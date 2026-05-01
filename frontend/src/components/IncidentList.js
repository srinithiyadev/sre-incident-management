import React, { useEffect, useState } from 'react';
import { getWorkitems, sendSignal } from '../api';

const COMPONENTS = [
  { id: 'RDBMS_PRIMARY_01',  type: 'RDBMS',  msg: 'Connection timeout — DB unreachable' },
  { id: 'CACHE_CLUSTER_01',  type: 'CACHE',  msg: 'Cache miss rate exceeded 90%' },
  { id: 'API_GATEWAY_01',    type: 'API',    msg: 'Latency spike p99 > 5000ms' },
  { id: 'MQ_BROKER_01',      type: 'MQ',     msg: 'Queue depth exceeded 100k' },
];

export default function IncidentList({ onSelect }) {
  const [items,    setItems]    = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [sending,  setSending]  = useState(false);

  const load = async () => {
    try {
      const res = await getWorkitems();
      setItems(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t); }, []);

  const simulateFailure = async (component) => {
    setSending(true);
    try {
      for (let i = 0; i < 5; i++) {
        await sendSignal({
          component_id:   component.id,
          component_type: component.type,
          error_message:  component.msg,
          severity:       'CRITICAL',
        });
      }
      await load();
    } catch (e) {
      alert('Error sending signal: ' + e.message);
    } finally {
      setSending(false);
    }
  };

  const counts = {
    total:        items.length,
    open:         items.filter(i => i.status === 'OPEN').length,
    investigating: items.filter(i => i.status === 'INVESTIGATING').length,
    resolved:     items.filter(i => i.status === 'RESOLVED').length,
  };

  return (
    <div>
      <div className="stats-bar">
        <div className="stat-card"><h4>Total</h4><p>{counts.total}</p></div>
        <div className="stat-card"><h4>Open</h4><p style={{color:'#fc8181'}}>{counts.open}</p></div>
        <div className="stat-card"><h4>Investigating</h4><p style={{color:'#f6ad55'}}>{counts.investigating}</p></div>
        <div className="stat-card"><h4>Resolved</h4><p style={{color:'#68d391'}}>{counts.resolved}</p></div>
      </div>

      <div style={{marginBottom:'1.5rem'}}>
        <p className="section-title">🧪 Simulate Failures</p>
        <div style={{display:'flex', gap:'0.5rem', flexWrap:'wrap'}}>
          {COMPONENTS.map(c => (
            <button
              key={c.id}
              className="btn-secondary"
              onClick={() => simulateFailure(c)}
              disabled={sending}
            >
              {sending ? '...' : `Trigger ${c.type}`}
            </button>
          ))}
        </div>
      </div>

      <p className="section-title">🔴 Live Incidents</p>

      {loading && <p style={{color:'#718096'}}>Loading...</p>}

      {!loading && items.length === 0 && (
        <p style={{color:'#718096'}}>No incidents. Click a button above to simulate a failure!</p>
      )}

      {items
        .sort((a, b) => a.priority.localeCompare(b.priority))
        .map(item => (
          <div key={item.id} className="card" onClick={() => onSelect(item.id)}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'flex-start'}}>
              <h3>{item.title}</h3>
              <span className={`badge ${item.priority}`}>{item.priority}</span>
            </div>
            <div className="card-meta">
              <span className={`badge ${item.status}`}>{item.status}</span>
              <span>Component: {item.component_id}</span>
              <span>Signals: {item.signal_count}</span>
              {item.mttr_minutes && <span>MTTR: {item.mttr_minutes.toFixed(1)} min</span>}
            </div>
          </div>
        ))}
    </div>
  );
}