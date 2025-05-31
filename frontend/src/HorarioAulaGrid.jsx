import React, { useEffect, useState } from "react";
import axios from "axios";
import AulaHorarioModal from "./AulaHorarioModal";

const DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
const HORAS = [
"07:00", "08:00", "09:00", "10:00", "11:00", "12:00",
"13:00", "14:00", "15:00", "16:00", "17:00", "18:00"
];

export default function HorarioAulaGrid() {
const [aulas, setAulas] = useState([]);
const [horarios, setHorarios] = useState([]);
const [modalData, setModalData] = useState({ show: false, aula: null, dia: "", hora: "" });

useEffect(() => {
    axios.get("/programacion/aulas/").then(res => setAulas(res.data));
    axios.get("/programacion/horarios/").then(res => setHorarios(res.data));
}, []);

  // Devuelve el horario asignado para un aula, día y hora
const getAsignacion = (aulaId, dia, hora) => {
    return horarios.find(
    h =>
        h.aula.id === aulaId &&
        h.dia === dia &&
        h.hora_inicio <= hora &&
        h.hora_fin > hora
    );
};

return (
    <div className="overflow-auto">
    <h2 className="text-xl font-bold mb-4">Grilla Semanal de Aulas</h2>
    <table className="min-w-full border text-xs">
        <thead>
        <tr>
            <th className="border px-2 py-1 bg-gray-100">Aula / Hora</th>
            {DIAS.map(dia => (
            <th key={dia} className="border px-2 py-1 bg-gray-100">{dia}</th>
            ))}
        </tr>
        </thead>
        <tbody>
        {aulas.map(aula => (
            HORAS.map(hora => (
            <tr key={aula.id + hora}>
                {hora === HORAS[0] && (
                <td className="border px-2 py-1 font-bold" rowSpan={HORAS.length}>
                    {aula.nombre}
                </td>
                )}
                <td className="border px-2 py-1 font-mono">{hora}</td>
                {DIAS.map(dia => {
                const asignacion = getAsignacion(aula.id, dia, hora);
                return (
                    <td key={dia} className={`border px-2 py-1 ${asignacion ? "bg-red-100" : "bg-green-100"}`}>
                    {asignacion
                        ? (
                        <div>
                            <div className="font-bold">{asignacion.asignatura.nombre}</div>
                            <div className="text-xs">{asignacion.seccion}</div>
                        </div>
                        )
                        : <button className="text-xs text-blue-600 underline"onClick={() => setModalData({ show: true, aula, dia, hora })}>Asignar</button>
                    }
                    </td>
                );
                })}
            </tr>
            ))
        ))}
        </tbody>
    </table>
    <AulaHorarioModal
show={modalData.show}
onClose={() => setModalData({ show: false, aula: null, dia: "", hora: "" })}
aula={modalData.aula}
dia={modalData.dia}
hora={modalData.hora}
onAsignar={() => {
    setModalData({ show: false, aula: null, dia: "", hora: "" });
    // Recarga los horarios
    axios.get("/programacion/horarios/").then(res => setHorarios(res.data));
}}
/>
    </div>
);
}