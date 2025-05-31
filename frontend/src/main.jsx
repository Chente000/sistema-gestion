import React from "react";
import { createRoot } from "react-dom/client";
import HorarioAulaGrid from "./HorarioAulaGrid";

const root = document.getElementById("aulario-root");
if (root) {
  createRoot(root).render(<HorarioAulaGrid />);
}
