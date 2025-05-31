// AulasList.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import AulaFormModal from "./AulaFormModal";

export default function AulasList() {
const [aulas, setAulas] = useState([]);
const [showModal, setShowModal] = useState(false);
const [editAula, setEditAula] = useState(null);

const fetchAulas = () => {
    axios.get("/programacion/aulas/").then(res => setAulas(res.data));
};

useEffect(() => {
    fetchAulas();
}, []);

const handleSave = (data) => {
    if (editAula) {
    axios.put(`/programacion/aulas/${editAula.id}/`, data).then(() => {
        setShowModal(false);
        setEditAula(null);
        fetchAulas();
    });
    } else {
    axios.post("/programacion/aulas/", data).then(() => {
        setShowModal(false);
        fetchAulas();
    });
    }
};

const handleDelete = (id) => {
    if (window.confirm("¿Seguro que deseas eliminar esta aula?")) {
    axios.delete(`/programacion/aulas/${id}/`).then(fetchAulas);
    }
};

return (
    <div className="p-4">
    <h2 className="text-xl font-bold mb-4">Aulas Registradas</h2>
    <button className="bg-green-600 text-white px-4 py-2 rounded mb-4" onClick={() => { setShowModal(true); setEditAula(null); }}>
        Agregar Aula
    </button>
    <table className="min-w-full bg-white border">
        <thead>
        <tr>
            <th className="border px-2 py-1">Nombre</th>
            <th className="border px-2 py-1">Tipo</th>
            <th className="border px-2 py-1">Capacidad</th>
            <th className="border px-2 py-1">Ubicación</th>
            <th className="border px-2 py-1">Acciones</th>
        </tr>
        </thead>
        <tbody>
        {aulas.map(aula => (
            <tr key={aula.id}>
            <td className="border px-2 py-1">{aula.nombre}</td>
            <td className="border px-2 py-1">{aula.tipo}</td>
            <td className="border px-2 py-1">{aula.capacidad}</td>
            <td className="border px-2 py-1">{aula.ubicacion}</td>
            <td className="border px-2 py-1 flex gap-2">
                <button className="bg-blue-500 text-white px-2 py-1 rounded" onClick={() => { setEditAula(aula); setShowModal(true); }}>Editar</button>
                <button className="bg-red-500 text-white px-2 py-1 rounded" onClick={() => handleDelete(aula.id)}>Eliminar</button>
            </td>
            </tr>
        ))}
        </tbody>
    </table>
    <AulaFormModal
        show={showModal}
        onClose={() => { setShowModal(false); setEditAula(null); }}
        onSave={handleSave}
        initialData={editAula}
    />
    </div>
);
}