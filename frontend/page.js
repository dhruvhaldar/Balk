"use client";
import React, { useState } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

export default function Home() {
    const [params, setParams] = useState({
        E: 210e9, G: 80e9,
        A: 1e-3, Iy: 1e-5, Iz: 1e-5, J: 1e-6, Cw: 1e-8,
        length: 2.0, n_elems: 10, load: 1000.0
    });
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setParams({ ...params, [e.target.name]: parseFloat(e.target.value) });
    };

    const runSimulation = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post('/api/solve', params);
            setResult(response.data);
        } catch (err) {
            console.error(err);
            setError('Simulation failed. Check console for details.');
        } finally {
            setLoading(false);
        }
    };

    // Prepare plot data
    let plotData = [];
    if (result) {
        plotData = [
            {
                x: result.x,
                y: result.uz,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Vertical Displacement (uz)',
            },
            {
                x: result.x,
                y: result.tx,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Twist Angle (tx)',
                yaxis: 'y2'
            }
        ];
    }

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
            <h1>Balk FEM Solver</h1>
            <div style={{ display: 'flex', gap: '20px' }}>
                <div style={{ width: '300px', flexShrink: 0 }}>
                    <h3>Parameters</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                        <label>E (Pa): <input name="E" type="number" value={params.E} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>G (Pa): <input name="G" type="number" value={params.G} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>A (m²): <input name="A" type="number" value={params.A} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>Iy (m⁴): <input name="Iy" type="number" value={params.Iy} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>Iz (m⁴): <input name="Iz" type="number" value={params.Iz} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>J (m⁴): <input name="J" type="number" value={params.J} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>Cw (m⁶): <input name="Cw" type="number" value={params.Cw} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>Length (m): <input name="length" type="number" value={params.length} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>Elements: <input name="n_elems" type="number" value={params.n_elems} onChange={handleChange} style={{ width: '100%' }} /></label>
                        <label>Load (N): <input name="load" type="number" value={params.load} onChange={handleChange} style={{ width: '100%' }} /></label>
                    </div>
                    <button onClick={runSimulation} disabled={loading} style={{ marginTop: '20px', padding: '10px', width: '100%' }}>
                        {loading ? 'Running...' : 'Run Simulation'}
                    </button>
                    {error && <p style={{ color: 'red' }}>{error}</p>}
                </div>

                <div style={{ flexGrow: 1 }}>
                    <h3>Results</h3>
                    {result ? (
                        <Plot
                            data={plotData}
                            layout={{
                                width: 800, height: 600,
                                title: 'Deformed Shape Setup',
                                xaxis: { title: 'Position x (m)' },
                                yaxis: { title: 'Displacement uz (m)' },
                                yaxis2: {
                                    title: 'Twist tx (rad)',
                                    overlaying: 'y',
                                    side: 'right'
                                }
                            }}
                        />
                    ) : (
                        <p>Run simulation to see results.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
