const VIAS = [
    "A",
    "B",
    "C",
    "D"
];


// =====================================================
// CRIAR CARDS
// =====================================================

function criarCards() {

    const grid =
        document.getElementById(
            "vias-grid"
        );


    VIAS.forEach(via => {

        grid.innerHTML += `

        <section
            class="via-card"
            id="card-${via}"
        >

            <div class="via-title">

                <h2>
                    Via ${via}
                </h2>

                <span
                    class="via-state"
                    id="estado-${via}"
                >
                    -
                </span>

            </div>


            <div class="traffic-light">

                <div
                    id="${via}-vermelho"
                    class="light red"
                ></div>

                <div
                    id="${via}-amarelo"
                    class="light yellow"
                ></div>

                <div
                    id="${via}-verde"
                    class="light green"
                ></div>

            </div>


            <div class="metrics">

                <div class="metric">

                    <span>
                        Veículos
                    </span>

                    <strong
                        id="veiculos-${via}"
                    >
                        —
                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Congestionamento
                    </span>

                    <strong
                        id="congestionamento-${via}"
                    >
                        Aguardando YOLO
                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Prioritário
                    </span>

                    <strong
                        id="prioritario-${via}"
                    >
                        —
                    </strong>

                </div>


                <div class="metric">

                    <span>
                        Tempo de espera
                    </span>

                    <strong
                        id="espera-${via}"
                    >
                        —
                    </strong>

                </div>

            </div>

        </section>

        `;
    });
}


// =====================================================
// COMPONENTES
// =====================================================

function atualizarStatus(
    id,
    valor
) {

    const elemento =
        document.getElementById(id);


    elemento.classList.remove(
        "online",
        "offline",
        "waiting"
    );


    if (valor === true) {

        elemento.classList.add(
            "online"
        );

    } else if (
        valor === false
    ) {

        elemento.classList.add(
            "offline"
        );

    } else {

        elemento.classList.add(
            "waiting"
        );
    }
}


// =====================================================
// SEMÁFORO
// =====================================================

function atualizarSemaforo(
    via,
    estado
) {

    const cores = [
        "vermelho",
        "amarelo",
        "verde"
    ];


    cores.forEach(cor => {

        document
            .getElementById(
                `${via}-${cor}`
            )
            .classList
            .remove("active");
    });


    if (
        cores.includes(
            estado
        )
    ) {

        document
            .getElementById(
                `${via}-${estado}`
            )
            .classList
            .add("active");
    }


    const label =
        document.getElementById(
            `estado-${via}`
        );


    label.textContent =
        estado.toUpperCase();


    const card =
        document.getElementById(
            `card-${via}`
        );


    card.classList.toggle(
        "green-active",
        estado === "verde"
    );
}


// =====================================================
// DADOS DO DASHBOARD
// =====================================================

function atualizarTela(
    dados
) {

    atualizarStatus(
        "status-bluetooth",
        dados.sistema.bluetooth
    );


    atualizarStatus(
        "status-camera",
        dados.sistema.camera
    );


    atualizarStatus(
        "status-yolo",
        dados.sistema.yolo
    );


    atualizarStatus(
        "status-fpga",
        dados.sistema.fpga
    );


    document.getElementById(
        "via-aberta"
    ).textContent =
        dados.via_aberta === "X"
        ? "Nenhuma"
        : `Via ${dados.via_aberta}`;


    document.getElementById(
        "ultima-deteccao"
    ).textContent =
        dados.ultima_deteccao
        ? `Via ${dados.ultima_deteccao}`
        : "Nenhuma";


    document.getElementById(
        "ultima-atualizacao"
    ).textContent =
        dados.ultima_atualizacao
        || "-";


    VIAS.forEach(via => {

        const dadosVia =
            dados.vias[via];


        atualizarSemaforo(
            via,
            dadosVia.semaforo
        );


        document.getElementById(
            `veiculos-${via}`
        ).textContent =
            dadosVia.veiculos
            ?? "—";


        document.getElementById(
            `congestionamento-${via}`
        ).textContent =
            dadosVia.congestionamento
            ?? "Aguardando YOLO";


        document.getElementById(
            `prioritario-${via}`
        ).textContent =
            dadosVia.veiculo_prioritario
            ? (
                dadosVia.tipo_prioritario
                ?? "Detectado"
            )
            : "Nenhum";


        document.getElementById(
            `espera-${via}`
        ).textContent =
            dadosVia.tempo_espera !== null
            ? `${dadosVia.tempo_espera}s`
            : "—";
    });
}


// =====================================================
// BUSCAR API
// =====================================================

async function carregarEstado() {

    try {

        const resposta =
            await fetch(
                "/api/status",
                {
                    cache:
                        "no-store"
                }
            );


        if (!resposta.ok) {

            throw new Error(
                "API indisponível"
            );
        }


        const dados =
            await resposta.json();


        atualizarTela(
            dados
        );

    } catch (erro) {

        console.error(
            "Erro ao atualizar dashboard:",
            erro
        );
    }
}


// =====================================================
// INICIAR
// =====================================================

criarCards();

carregarEstado();


// Atualiza duas vezes por segundo
setInterval(
    carregarEstado,
    500
);
