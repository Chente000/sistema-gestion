import React, { useEffect, useState } from "react";
import axios from "axios";

export default function AulaHorarioModal({ show, onClose, aula, dia, hora, onAsignar }) {
const [asignaturas, setAsignaturas] = useState([]);
const [carreras, setCarreras] = useState([]);
const [form, setForm] = useState({
    asignatura: "",
    carrera: "",
    seccion: "",
    semestre: "",
    hora_inicio: hora,
    hora_fin: "",
});
const [error, setError] = useState("");

useEffect(() => {
    if (show) {
    axios.get("/programacion/asignaturas/").then(res => setAsignaturas(res.data));
    axios.get("/programacion/carreras/").then(res => setCarreras(res.data));
    setForm(f => ({ ...f, hora_inicio: hora, hora_fin: "" }));
    setError("");
    }
}, [show, hora]);

if (!show) return null;

const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
};

const handleSubmit = e => {
    e.preventDefault();
    setError("");
    axios.post("/programacion/horarios/", {
    aula: aula.id,
    dia,
    hora_inicio: form.hora_inicio,
    hora_fin: form.hora_fin,
    asignatura: form.asignatura,
    carrera: form.carrera,
    seccion: form.seccion,
    semestre: form.semestre,
    })
    .then(() => {
        onAsignar();
        onClose();
    })
    .catch(err => {
        setError(err.response?.data?.detail || "Error al asignar horario.");
    });
};

return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
        <h3 className="text-lg font-bold mb-4">Asignar Materia a {aula.nombre} - {dia} {hora}</h3>
        <form onSubmit={handleSubmit}>
        <div className="mb-2">
            <label className="block">Carrera</label>
            <select name="carrera" value={form.carrera} onChange={handleChange} className="border w-full px-2 py-1" required>
            <option value="">Seleccione...</option>
            {carreras.map(c => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
            </select>
        </div>
        <div className="mb-2">
            <label className="block">Asignatura</label>
            <select name="asignatura" value={form.asignatura} onChange={handleChange} className="border w-full px-2 py-1" required>
            <option value="">Seleccione...</option>
            {asignaturas
                .filter(a => !form.carrera || a.carrera === form.carrera)
                .map(a => (
                <option key={a.id} value={a.id}>{a.nombre}</option>
                ))}
            </select>
        </div>
        <div className="mb-2">
            <label className="block">Sección</label>
            <input name="seccion" value={form.seccion} onChange={handleChange} className="border w-full px-2 py-1" required />
        </div>
        <div className="mb-2">
            <label className="block">Semestre</label>
            <input name="semestre" value={form.semestre} onChange={handleChange} className="border w-full px-2 py-1" />
        </div>
        <div className="mb-2 flex gap-2">
            <div>
            <label className="block">Hora inicio</label>
            <input name="hora_inicio" type="time" value={form.hora_inicio} onChange={handleChange} className="border w-full px-2 py-1" required />
            </div>
            <div>
            <label className="block">Hora fin</label>
            <input name="hora_fin" type="time" value={form.hora_fin} onChange={handleChange} className="border w-full px-2 py-1" required />
            </div>
        </div>
        {error && <div className="text-red-600 text-sm mb-2">{error}</div>}
        <div className="flex justify-end gap-2 mt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded">Asignar</button>
        </div>
        </form>
    </div>
    </div>
);
}