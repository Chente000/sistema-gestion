import React, { useState, useEffect } from "react";

export default function AulaFormModal({ show, onClose, onSave, initialData }) {
const [form, setForm] = useState({
    nombre: "",
    tipo: "Teórica",
    capacidad: "",
    ubicacion: "",
    observaciones: ""
});

useEffect(() => {
    if (initialData) setForm(initialData);
    else setForm({
    nombre: "",
    tipo: "Teórica",
    capacidad: "",
    ubicacion: "",
    observaciones: ""
    });
}, [initialData, show]);

if (!show) return null;

const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
};

const handleSubmit = e => {
    e.preventDefault();
    onSave(form);
};

return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
    <div className="bg-white p-6 rounded shadow-lg w-full max-w-md">
        <h3 className="text-lg font-bold mb-4">{initialData ? "Editar Aula" : "Agregar Aula"}</h3>
        <form onSubmit={handleSubmit}>
        <div className="mb-2">
            <label className="block">Nombre</label>
            <input name="nombre" value={form.nombre} onChange={handleChange} className="border w-full px-2 py-1" required />
        </div>
        <div className="mb-2">
            <label className="block">Tipo</label>
            <select name="tipo" value={form.tipo} onChange={handleChange} className="border w-full px-2 py-1">
            <option value="Teórica">Teórica</option>
            <option value="Laboratorio">Laboratorio</option>
            <option value="Auditorio">Auditorio</option>
            <option value="Otro">Otro</option>
            </select>
        </div>
        <div className="mb-2">
            <label className="block">Capacidad</label>
            <input name="capacidad" type="number" value={form.capacidad} onChange={handleChange} className="border w-full px-2 py-1" required />
        </div>
        <div className="mb-2">
            <label className="block">Ubicación</label>
            <input name="ubicacion" value={form.ubicacion} onChange={handleChange} className="border w-full px-2 py-1" />
        </div>
        <div className="mb-2">
            <label className="block">Observaciones</label>
            <textarea name="observaciones" value={form.observaciones} onChange={handleChange} className="border w-full px-2 py-1" />
        </div>
        <div className="flex justify-end gap-2 mt-4">
            <button type="button" onClick={onClose} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded">{initialData ? "Guardar" : "Agregar"}</button>
        </div>
        </form>
    </div>
    </div>
);
}