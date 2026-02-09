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

    // Common input style
    const inputStyle = {
        padding: '8px',
        borderRadius: '4px',
        border: '1px solid #ccc',
        width: '100%',
        boxSizing: 'border-box'
    };

    return (
        <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
            <h1 style={{ marginBottom: '30px', borderBottom: '2px solid #333', paddingBottom: '10px' }}>
                Balk FEM Solver
            </h1>

            <div style={{ display: 'flex', gap: '40px', flexWrap: 'wrap' }}>
                {/* Input Panel */}
                <div style={{ flex: '1 1 300px', padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '8px', height: 'fit-content' }}>
                    <h3 style={{ marginTop: 0 }}>Beam Parameters</h3>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '15px' }}>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>E (Pa)</div>
                            <input name="E" type="number" value={params.E} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>G (Pa)</div>
                            <input name="G" type="number" value={params.G} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>A (m²)</div>
                            <input name="A" type="number" value={params.A} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>Iy (m⁴)</div>
                            <input name="Iy" type="number" value={params.Iy} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>Iz (m⁴)</div>
                            <input name="Iz" type="number" value={params.Iz} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>J (m⁴)</div>
                            <input name="J" type="number" value={params.J} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>Cw (m⁶)</div>
                            <input name="Cw" type="number" value={params.Cw} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>Length (m)</div>
                            <input name="length" type="number" value={params.length} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>Elements</div>
                            <input name="n_elems" type="number" value={params.n_elems} onChange={handleChange} style={inputStyle} />
                        </label>
                        <label>
                            <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>Load Pz (N)</div>
                            <input name="load" type="number" value={params.load} onChange={handleChange} style={inputStyle} />
                        </label>
                    </div>

                    <button
                        onClick={runSimulation}
                        disabled={loading}
                        style={{
                            marginTop: '25px',
                            padding: '12px 20px',
                            width: '100%',
                            backgroundColor: loading ? '#ccc' : '#0070f3',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '1em',
                            fontWeight: 'bold',
                            cursor: loading ? 'not-allowed' : 'pointer'
                        }}>
                        {loading ? 'Running Analysis...' : 'Run Simulation'}
                    </button>

                    {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
                </div>

                {/* Results Panel */}
                <div style={{ flex: '2 1 500px' }}>
                    <h3 style={{ marginTop: 0 }}>Simulation Results</h3>
                    {result ? (
                        <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '10px' }}>
                            <Plot
                                data={plotData}
                                layout={{
                                    autosize: true,
                                    height: 500,
                                    title: 'Displacement Profile',
                                    xaxis: { title: 'Position x (m)' },
                                    yaxis: { title: 'Vertical Displacement uz (m)' },
                                    yaxis2: {
                                        title: 'Twist Angle tx (rad)',
                                        overlaying: 'y',
                                        side: 'right'
                                    },
                                    legend: { x: 0.1, y: 1.1, orientation: 'h' },
                                    margin: { l: 50, r: 50, t: 50, b: 50 }
                                }}
                                useResizeHandler={true}
                                style={{ width: "100%", height: "100%" }}
                            />
                        </div>
                    ) : (
                        <div style={{
                            height: '500px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: '1px dashed #ccc',
                            borderRadius: '8px',
                            color: '#666'
                        }}>
                            Click "Run Simulation" to visualize the deformed shape.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
