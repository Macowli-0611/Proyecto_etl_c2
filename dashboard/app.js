/* ==========================================================================
   ETL Analytics Dashboard — Interactive Application Logic (app.js)
   ========================================================================== */

document.addEventListener("DOMContentLoaded", async () => {
    // 1. Tab Switching Logic
    const navButtons = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const viewTitle = document.getElementById("view-title");

    const tabTitles = {
        "tab-overview": "Resumen Ejecutivo & Métricas de Integración",
        "tab-api-integration": "Requerimiento R6: Carga y Presión Institucional (API)",
        "tab-legal-gap": "Requerimiento R7: Brecha Legal (Ley 2126) vs Severidad (API)",
        "tab-baseline-r1-r5": "Línea Base Reconciliada (Requerimientos R1 a R5)",
        "tab-traceability": "Arquitectura de Calidad, Compuertas GX y Confiabilidad"
    };

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            navButtons.forEach(b => b.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            const targetId = btn.getAttribute("data-tab");
            document.getElementById(targetId).classList.add("active");

            if (tabTitles[targetId]) {
                viewTitle.textContent = tabTitles[targetId];
            }
        });
    });

    // 2. Fetch Live/Cached DW Data Payload
    let dwData = null;
    try {
        const response = await fetch("data_dw.json");
        if (response.ok) {
            dwData = await response.json();
            console.log("Loaded DW analytical payload:", dwData);
        } else {
            console.warn("Could not fetch data_dw.json. Using fallback embedded data.");
        }
    } catch (err) {
        console.error("Error loading data_dw.json:", err);
    }

    if (!dwData) {
        alert("No se pudo cargar el archivo data_dw.json. Verifique la conexión con el Data Warehouse.");
        return;
    }

    // 3. Render KPIs
    document.getElementById("val-total-victimas").textContent = dwData.kpis.total_victimas.toLocaleString();
    document.getElementById("val-total-hechos").textContent = dwData.kpis.total_fact_rows.toLocaleString();
    document.getElementById("val-total-comisarias").textContent = dwData.kpis.total_comisarias_instaladas.toLocaleString();
    document.getElementById("val-total-brecha").textContent = dwData.kpis.total_brecha_comisarias.toLocaleString();

    // Chart.js default theme configuration
    Chart.defaults.color = "#94A3B8";
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;

    // 4. Render R1 Chart (Temporal)
    const ctxR1 = document.getElementById("chart-r1-overview").getContext("2d");
    new Chart(ctxR1, {
        type: "line",
        data: {
            labels: dwData.r1_temporal.map(d => d.anio),
            datasets: [
                {
                    label: "Víctimas Totales",
                    data: dwData.r1_temporal.map(d => d.victimas),
                    borderColor: "#38BDF8",
                    backgroundColor: "rgba(56, 189, 248, 0.15)",
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointRadius: 4,
                    pointBackgroundColor: "#38BDF8"
                },
                {
                    label: "Denuncias Policiales",
                    data: dwData.r1_temporal.map(d => d.denuncias),
                    borderColor: "#818CF8",
                    borderDash: [5, 5],
                    borderWidth: 1.5,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
                x: { grid: { display: false } }
            }
        }
    });

    // 5. Render R6 Overview & Detail Chart
    const topR6 = dwData.r6_institutional_pressure.slice(0, 8);
    const ctxR6Overview = document.getElementById("chart-r6-overview").getContext("2d");
    new Chart(ctxR6Overview, {
        type: "bar",
        data: {
            labels: topR6.map(d => d.municipio),
            datasets: [{
                label: "Víctimas por Comisaría Instalada",
                data: topR6.map(d => d.victimas_por_comisaria),
                backgroundColor: [
                    "#EF4444", "#F97316", "#F59E0B", "#10B981",
                    "#06B6D4", "#6366F1", "#8B5CF6", "#EC4899"
                ],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
                x: { grid: { display: false } }
            }
        }
    });

    // R6 Detail Chart
    const ctxR6Detail = document.getElementById("chart-r6-detail").getContext("2d");
    new Chart(ctxR6Detail, {
        type: "bar",
        data: {
            labels: dwData.r6_institutional_pressure.map(d => d.municipio),
            datasets: [{
                label: "Carga Operativa (Víctimas / Comisaría)",
                data: dwData.r6_institutional_pressure.map(d => d.victimas_por_comisaria),
                backgroundColor: "rgba(244, 63, 94, 0.75)",
                borderColor: "#F43F5E",
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
                y: { grid: { display: false } }
            }
        }
    });

    // R6 Distribution Doughnut
    const ctxR6Dist = document.getElementById("chart-r6-distribution").getContext("2d");
    new Chart(ctxR6Dist, {
        type: "doughnut",
        data: {
            labels: ["Sobrecarga Crítica (>2k)", "Sobrecarga Alta (1k-2k)", "Carga Moderada (<1k)"],
            datasets: [{
                data: [35, 78, 989],
                backgroundColor: ["#EF4444", "#F59E0B", "#10B981"],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });

    // Populate R6 Table
    const tbodyR6 = document.getElementById("tbody-r6");
    dwData.r6_institutional_pressure.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><code>${row.codigo}</code></td>
            <td><strong>${row.municipio}</strong></td>
            <td>${row.departamento}</td>
            <td>Cat. ${row.categoria}</td>
            <td>${row.comisarias}</td>
            <td>${row.victimas.toLocaleString()}</td>
            <td><strong style="color: #F87171;">${row.victimas_por_comisaria.toLocaleString()}</strong></td>
            <td><span class="badge-priority p1">${row.nivel_presion}</span></td>
        `;
        tbodyR6.appendChild(tr);
    });

    // 6. Render R7 Charts (Legal Gap vs Severity)
    const ctxR7Cat = document.getElementById("chart-r7-categories").getContext("2d");
    new Chart(ctxR7Cat, {
        type: "bar",
        data: {
            labels: dwData.r7_category_summary.map(d => `Cat. ${d.categoria}`),
            datasets: [
                {
                    label: "Comisarías Requeridas (Ley 2126)",
                    data: dwData.r7_category_summary.map(d => d.requeridas),
                    backgroundColor: "#38BDF8",
                    borderRadius: 4
                },
                {
                    label: "Comisarías Instaladas",
                    data: dwData.r7_category_summary.map(d => d.instaladas),
                    backgroundColor: "#10B981",
                    borderRadius: 4
                },
                {
                    label: "Déficit / Brecha Legal",
                    data: dwData.r7_category_summary.map(d => d.brecha),
                    backgroundColor: "#F43F5E",
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { grid: { color: "rgba(255, 255, 255, 0.05)" } },
                x: { grid: { display: false } }
            }
        }
    });

    // R7 Scatter / Bubble
    const ctxR7Scatter = document.getElementById("chart-r7-scatter").getContext("2d");
    new Chart(ctxR7Scatter, {
        type: "bubble",
        data: {
            datasets: [{
                label: "Municipios con Déficit Legal",
                data: dwData.r7_legal_gap_priorities.map(d => ({
                    x: d.brecha,
                    y: d.menores_letal,
                    r: Math.min(25, Math.max(6, Math.sqrt(d.total_victimas) / 10)),
                    name: d.municipio
                })),
                backgroundColor: "rgba(244, 63, 94, 0.65)",
                borderColor: "#FDA4AF",
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.raw.name}: Brecha ${ctx.raw.x} comisarías, ${ctx.raw.y} menores agredidos con arma letal`
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: "Brecha Legal de Comisarías (Ley 2126)" },
                    grid: { color: "rgba(255, 255, 255, 0.05)" }
                },
                y: {
                    title: { display: true, text: "Menores Atacados con Armas Letales (R5)" },
                    grid: { color: "rgba(255, 255, 255, 0.05)" }
                }
            }
        }
    });

    // Populate R7 Table
    const tbodyR7 = document.getElementById("tbody-r7");
    dwData.r7_legal_gap_priorities.forEach(row => {
        const tr = document.createElement("tr");
        const priorityClass = row.prioridad.includes("1") ? "p1" : (row.prioridad.includes("2") ? "p2" : "p3");
        tr.innerHTML = `
            <td><strong>${row.municipio}</strong></td>
            <td>${row.departamento}</td>
            <td>${row.comisarias_instaladas}</td>
            <td>${row.comisarias_requeridas}</td>
            <td><strong style="color: #F87171;">-${row.brecha}</strong></td>
            <td>${row.menores_letal}</td>
            <td>${row.mujeres.toLocaleString()}</td>
            <td><span class="badge-priority ${priorityClass}">${row.prioridad}</span></td>
        `;
        tbodyR7.appendChild(tr);
    });

    // 7. Render Baseline Charts (R2, R3, R4, R5)
    // R2: Territorial
    const ctxR2 = document.getElementById("chart-r2").getContext("2d");
    new Chart(ctxR2, {
        type: "bar",
        data: {
            labels: dwData.r2_territorial.slice(0, 7).map(d => d.departamento),
            datasets: [
                {
                    label: "Víctimas en Capital (CT)",
                    data: dwData.r2_territorial.slice(0, 7).map(d => d.victimas_capital),
                    backgroundColor: "#38BDF8"
                },
                {
                    label: "Resto del Departamento",
                    data: dwData.r2_territorial.slice(0, 7).map(d => d.total_victimas - d.victimas_capital),
                    backgroundColor: "#1E293B",
                    borderColor: "rgba(255,255,255,0.1)",
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: true, grid: { display: false } },
                y: { stacked: true, grid: { color: "rgba(255, 255, 255, 0.05)" } }
            }
        }
    });

    // R3: Demographics
    const ctxR3 = document.getElementById("chart-r3").getContext("2d");
    new Chart(ctxR3, {
        type: "doughnut",
        data: {
            labels: dwData.r3_demographics.slice(0, 5).map(d => d.perfil),
            datasets: [{
                data: dwData.r3_demographics.slice(0, 5).map(d => d.victimas),
                backgroundColor: ["#EC4899", "#8B5CF6", "#38BDF8", "#F59E0B", "#64748B"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } }
        }
    });

    // R4: Mechanisms
    const ctxR4 = document.getElementById("chart-r4").getContext("2d");
    new Chart(ctxR4, {
        type: "pie",
        data: {
            labels: dwData.r4_mechanisms.map(d => d.categoria),
            datasets: [{
                data: dwData.r4_mechanisms.map(d => d.victimas),
                backgroundColor: ["#38BDF8", "#F97316", "#EF4444", "#64748B", "#A855F7", "#10B981"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } }
        }
    });

    // R5 Table
    const tbodyR5 = document.getElementById("tbody-r5");
    dwData.r5_minor_hotspots.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${row.municipio}</strong></td>
            <td>${row.departamento}</td>
            <td><strong style="color: #F87171;">${row.menores_letal} menores</strong></td>
            <td><span class="badge-priority p1">FOCO ROJO (ICBF)</span></td>
        `;
        tbodyR5.appendChild(tr);
    });
});
