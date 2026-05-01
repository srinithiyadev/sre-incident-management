import React, { useState } from 'react';
import { submitRCA } from '../api';

const CATEGORIES = [
  'Database Failure',
  'Network Issue',
  'Cache Failure',
  'API Degradation',
  'Queue Overflow',
  'Security Incident',
  'Infrastructure',
  'Unknown',
];

export default function RCAForm({ workitemId, onSubmitted }) {
  const [form, setForm] = useState({
    root_cause:       '',
    category:         CATEGORIES[0],
    fix_applied:      '',
    prevention_steps: '',
    incident_start:   '',
    incident_end:     '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error,      setError]      = useState('');

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async () => {
    if (!form.root_cause || !form.fix_applied || !form.prevention_steps || !form.incident_start || !form.incident_end) {
      setError('All fields are required!');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await submitRCA(workitemId, {
        ...form,
        incident_start: new Date(form.incident_start).toISOString(),
        incident_end:   new Date(form.incident_end).toISOString(),
      });
      onSubmitted();
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="card" style={{cursor:'default', marginTop:'1rem'}}>
      <p className="section-title">📋 Root Cause Analysis</p>

      {error && <p style={{color:'#fc8181', marginBottom:'1rem'}}>{error}</p>}

      <div className="form-group">
        <label>Root Cause Category</label>
        <select name="category" value={form.category} onChange={handle}>
          {CATEGORIES.map(c => <option key={c}>{c}</option>)}
        </select>
      </div>

      <div className="form-group">
        <label>Root Cause Description</label>
        <textarea name="root_cause" value={form.root_cause} onChange={handle} placeholder="What caused this incident?" />
      </div>

      <div className="form-group">
        <label>Fix Applied</label>
        <textarea name="fix_applied" value={form.fix_applied} onChange={handle} placeholder="What fix was applied?" />
      </div>

      <div className="form-group">
        <label>Prevention Steps</label>
        <textarea name="prevention_steps" value={form.prevention_steps} onChange={handle} placeholder="How to prevent this in future?" />
      </div>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem'}}>
        <div className="form-group">
          <label>Incident Start</label>
          <input type="datetime-local" name="incident_start" value={form.incident_start} onChange={handle} />
        </div>
        <div className="form-group">
          <label>Incident End</label>
          <input type="datetime-local" name="incident_end" value={form.incident_end} onChange={handle} />
        </div>
      </div>

      <button className="btn-success" onClick={handleSubmit} disabled={submitting}>
        {submitting ? 'Submitting...' : 'Submit RCA'}
      </button>
    </div>
  );
}